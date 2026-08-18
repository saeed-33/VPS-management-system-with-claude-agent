"""
قراءة مخرجات Claude بصيغة JSON المفردة أو stream-json.

تستخرج معرف الجلسة والنتيجة والعدادات والأدوات وخوادم MCP، وترفض الجلسة التي
لا تثبت اتصال أداة VPS وتنفيذ الفحوص التشغيلية المطلوبة.
"""
from __future__ import annotations

import json

from app.runtime.claude.exceptions import ClaudeProcessOutputError
from app.runtime.claude.models import ClaudeRawResult


class ClaudeCliJsonDecoder:
    """
    محلل يتحقق من بنية مخرجات Claude ويستخرج منها دليل تنفيذ دورة VPS التشغيلية.
    """

    _REQUIRED_VPS_TOOLS = frozenset(
        {
            "mcp__vps__run_monitoring",
            "mcp__vps__analyze_report",
        }
    )

    def decode(
        self,
        stdout: str,
    ) -> ClaudeRawResult:
        """
        يحدد شكل مخرج Claude ثم يحوله إلى نتيجة خام سواء كان JSON مفردًا أو stream من الأحداث.
        """
        events = self._parse_stdout(
            stdout
        )

        if isinstance(events, dict):
            return self._decode_single_envelope(
                events
            )

        return self._decode_event_sequence(
            events
        )

    def _parse_stdout(
        self,
        stdout: str,
    ) -> dict | list[dict]:
        """
        يفك JSON المفرد أو الدفعة أو الأسطر المتتابعة ويرفض المخرج الفارغ أو غير الصالح.
        """
        stripped = stdout.strip()

        if not stripped:
            raise ClaudeProcessOutputError(
                "Claude process returned empty stdout."
            )

        # نقبل شكل الرسالة المفردة أو الدفعة التي قد تعيدها جلسة Claude.
        try:
            payload = json.loads(
                stripped
            )
        except json.JSONDecodeError:
            payload = None

        if isinstance(payload, dict):
            return payload

        if isinstance(payload, list):
            if not all(
                isinstance(item, dict)
                for item in payload
            ):
                raise ClaudeProcessOutputError(
                    "Claude JSON event array must contain only objects."
                )
            return payload

        # تصل أحداث الجلسة كسجلات JSON مفصولة بأسطر.
        events: list[dict] = []

        for line_number, line in enumerate(
            stdout.splitlines(),
            start=1,
        ):
            candidate = line.strip()

            if not candidate:
                continue

            try:
                event = json.loads(
                    candidate
                )
            except json.JSONDecodeError as exc:
                raise ClaudeProcessOutputError(
                    "Claude stream-json contained invalid JSON "
                    f"on line {line_number}."
                ) from exc

            if not isinstance(event, dict):
                raise ClaudeProcessOutputError(
                    "Claude stream-json lines must be JSON objects."
                )

            events.append(event)

        if not events:
            raise ClaudeProcessOutputError(
                "Claude stream-json contained no events."
            )

        return events

    def _decode_single_envelope(
        self,
        payload: dict,
    ) -> ClaudeRawResult:
        """
        يستخرج الجلسة والنتيجة والعدادات من غلاف JSON واحد بعد فحص خطئه.
        """
        session_id = self._session_id(
            payload
        )

        self._raise_for_result_error(
            payload
        )

        content = self._content_from_envelope(
            payload
        )

        return ClaudeRawResult(
            session_id=session_id,
            content=content,
            turn_count=self._non_negative_int(
                payload,
                "num_turns",
                fallback_key="turn_count",
            ),
            tool_call_count=self._non_negative_int(
                payload,
                "tool_call_count",
            ),
            usage_metadata=self._usage_metadata(
                payload
            ),
        )

    def _decode_event_sequence(
        self,
        events: list[dict],
    ) -> ClaudeRawResult:
        """
        يطابق أحداث البدء والنتيجة ويتحقق من ثبات معرف الجلسة قبل إنشاء المخرج الخام.
        """
        init_events = [
            event
            for event in events
            if (
                event.get("type") == "system"
                and event.get("subtype") == "init"
            )
        ]

        if len(init_events) != 1:
            raise ClaudeProcessOutputError(
                "Claude event stream must contain exactly "
                "one system/init event."
            )

        result_events = [
            event
            for event in events
            if event.get("type") == "result"
        ]

        if len(result_events) != 1:
            raise ClaudeProcessOutputError(
                "Claude event stream must contain exactly "
                "one result event."
            )

        init_event = init_events[0]
        result_event = result_events[0]

        init_session_id = self._session_id(
            init_event
        )
        result_session_id = self._session_id(
            result_event
        )

        if init_session_id != result_session_id:
            raise ClaudeProcessOutputError(
                "Claude event stream session_id mismatch."
            )

        self._raise_for_result_error(
            result_event
        )

        tool_names = self._event_tool_names(
            events
        )

        mcp_servers = self._mcp_servers(
            init_event
        )

        vps_server = next(
            (
                item
                for item in mcp_servers
                if item.get("name") == "vps"
            ),
            None,
        )

        if vps_server is not None:
            content = self._operational_vps_content(
                session_id=result_session_id,
                vps_server=vps_server,
                tool_names=tool_names,
            )
        else:
            content = self._event_content(
                result_event=result_event,
                events=events,
            )

        usage_metadata = self._usage_metadata(
            result_event
        )

        if tool_names:
            usage_metadata[
                "event_tool_names"
            ] = tool_names

        if mcp_servers:
            usage_metadata[
                "event_mcp_servers"
            ] = mcp_servers

        return ClaudeRawResult(
            session_id=result_session_id,
            content=content,
            turn_count=self._non_negative_int(
                result_event,
                "num_turns",
                fallback_key="turn_count",
            ),
            tool_call_count=max(
                self._non_negative_int(
                    result_event,
                    "tool_call_count",
                ),
                len(tool_names),
            ),
            usage_metadata=usage_metadata,
        )

    def _operational_vps_content(
        self,
        *,
        session_id: str,
        vps_server: dict,
        tool_names: list[str],
    ) -> str:
        """
        يثبت اتصال خادم VPS واستدعاء أدوات المراقبة المطلوبة ثم يبني نتيجة تشغيل موثقة.
        """
        status = vps_server.get(
            "status"
        )

        if status != "connected":
            raise ClaudeProcessOutputError(
                "Claude operational session cannot be accepted: "
                f"vps MCP status={status!r}."
            )

        used = set(
            tool_names
        )
        missing = sorted(
            self._REQUIRED_VPS_TOOLS
            - used
        )

        if missing:
            raise ClaudeProcessOutputError(
                "Claude operational session cannot be accepted: "
                "required project MCP tools were not called: "
                + ", ".join(missing)
                + "; observed tool calls: "
                + (
                    ", ".join(tool_names)
                    if tool_names
                    else "none"
                )
            )

        # هذا الغلاف ليس تشخيصًا؛ التقرير والتحليل والتحقيق والأدلة محفوظة في
        # حالة المشروع. وظيفته إثبات أن مسارًا تشغيليًا محدودًا نفذ فعلًا.
        envelope = {
            "status": "completed",
            "summary": (
                "Claude operational monitoring cycle completed "
                "through the project MCP boundary."
            ),
            "data": {
                "session_id": session_id,
                "required_tools_verified": sorted(
                    self._REQUIRED_VPS_TOOLS
                ),
                "tool_calls": list(
                    tool_names
                ),
            },
            "metadata": {
                "result_source": (
                    "runtime_mcp_evidence"
                ),
                "mcp_server": "vps",
                "mcp_status": status,
            },
        }

        return json.dumps(
            envelope,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def _event_content(
        self,
        *,
        result_event: dict,
        events: list[dict],
    ) -> str:
        """
        يستخرج المحتوى من حدث النتيجة أو يستخدم آخر نص مساعد آمن عند غياب الحقل المتوقع.
        """
        try:
            return self._content_from_envelope(
                result_event
            )
        except ClaudeProcessOutputError as exc:
            text = self._final_assistant_text(
                events
            )

            if text is None:
                raise ClaudeProcessOutputError(
                    "Claude successful event stream contained "
                    "no safe final assistant text."
                ) from exc

            return text

    @staticmethod
    def _final_assistant_text(
        events: list[dict],
    ) -> str | None:
        """
        يبحث من نهاية الأحداث عن نص مساعد نهائي لا يزال يطلب أداة أخرى.
        """
        for event in reversed(
            events
        ):
            if event.get("type") != "assistant":
                continue

            message = event.get(
                "message"
            )

            if not isinstance(
                message,
                dict,
            ):
                continue

            content = message.get(
                "content"
            )

            if not isinstance(
                content,
                list,
            ):
                continue

            # لا نعد رسالة طلب أداة في منتصف الجلسة جوابًا نهائيًا.
            if any(
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                for block in content
            ):
                continue

            text_parts = [
                block.get(
                    "text",
                    "",
                )
                for block in content
                if (
                    isinstance(
                        block,
                        dict,
                    )
                    and block.get(
                        "type"
                    )
                    == "text"
                    and isinstance(
                        block.get(
                            "text"
                        ),
                        str,
                    )
                    and block.get(
                        "text"
                    ).strip()
                )
            ]

            text = "".join(
                text_parts
            ).strip()

            if text:
                return text

        return None

    @staticmethod
    def _event_tool_names(
        events: list[dict],
    ) -> list[str]:
        """
        يجمع أسماء الأدوات التي طلبتها الجلسة من أحداث المساعد لاستخدامها في التحقق والتتبع.
        """
        names: list[str] = []

        for event in events:
            if event.get("type") != "assistant":
                continue

            message = event.get(
                "message"
            )

            if not isinstance(
                message,
                dict,
            ):
                continue

            content = message.get(
                "content"
            )

            if not isinstance(
                content,
                list,
            ):
                continue

            for block in content:
                if not isinstance(
                    block,
                    dict,
                ):
                    continue

                if (
                    block.get("type")
                    != "tool_use"
                ):
                    continue

                name = block.get(
                    "name"
                )

                if (
                    isinstance(
                        name,
                        str,
                    )
                    and name.strip()
                ):
                    names.append(
                        name.strip()
                    )

        return names

    @staticmethod
    def _mcp_servers(
        init_event: dict,
    ) -> list[dict]:
        """
        يستخرج قائمة خوادم MCP من حدث بدء الجلسة بصيغة آمنة.
        """
        value = init_event.get(
            "mcp_servers",
            [],
        )

        if not isinstance(
            value,
            list,
        ):
            return []

        return [
            dict(item)
            for item in value
            if isinstance(
                item,
                dict,
            )
        ]

    @staticmethod
    def _session_id(
        payload: dict,
    ) -> str:
        """
        يقرأ معرف الجلسة ويمنع قبول مخرج لا يمكن ربطه بمهمة محددة.
        """
        value = payload.get(
            "session_id"
        )

        if (
            not isinstance(
                value,
                str,
            )
            or not value.strip()
        ):
            raise ClaudeProcessOutputError(
                "Claude output is missing session_id."
            )

        return value.strip()

    @staticmethod
    def _raise_for_result_error(
        payload: dict,
    ) -> None:
        """
        يفحص حالة حدث النتيجة ويرفع فشلًا إذا أعلنت Claude نهاية غير ناجحة.
        """
        if payload.get(
            "type"
        ) != "result":
            return

        subtype = payload.get(
            "subtype"
        )
        is_error = payload.get(
            "is_error"
        )

        if (
            isinstance(
                subtype,
                str,
            )
            and subtype
            and subtype != "success"
        ):
            raise ClaudeProcessOutputError(
                "Claude result reported failure: "
                f"subtype={subtype}; "
                f"num_turns={payload.get('num_turns')}; "
                f"stop_reason={payload.get('stop_reason')}; "
                f"is_error={is_error}; "
                f"session_id={payload.get('session_id')}"
            )

        if is_error is True:
            raise ClaudeProcessOutputError(
                "Claude result reported is_error=true "
                f"with subtype={subtype!r}."
            )

    @staticmethod
    def _content_from_envelope(
        payload: dict,
    ) -> str:
        """
        يستخرج JSON المنظم أو النص النهائي من غلاف النتيجة ويخفق عند غيابهما.
        """
        structured = payload.get(
            "structured_output"
        )

        if structured is not None:
            if not isinstance(
                structured,
                dict,
            ):
                raise ClaudeProcessOutputError(
                    "structured_output must be an object."
                )

            return json.dumps(
                structured,
                ensure_ascii=False,
                separators=(",", ":"),
            )

        result = payload.get(
            "result"
        )

        if (
            not isinstance(
                result,
                str,
            )
            or not result.strip()
        ):
            raise ClaudeProcessOutputError(
                "Claude successful output does not contain "
                "structured_output or a non-empty result."
            )

        return result

    @staticmethod
    def _non_negative_int(
        payload: dict,
        key: str,
        *,
        fallback_key: str | None = None,
    ) -> int:
        """
        يقرأ عدادًا غير سالب مع دعم اسم بديل وإظهار القيمة غير الصالحة كخطأ.
        """
        value = payload.get(
            key
        )

        if (
            value is None
            and fallback_key is not None
        ):
            value = payload.get(
                fallback_key
            )

        if value is None:
            return 0

        if (
            not isinstance(
                value,
                int,
            )
            or isinstance(
                value,
                bool,
            )
            or value < 0
        ):
            raise ClaudeProcessOutputError(
                f"{key} must be a non-negative integer."
            )

        return value

    @staticmethod
    def _usage_metadata(
        payload: dict,
    ) -> dict:
        """
        يجمع بيانات الاستخدام وحالة التوقف من مخرج الجلسة في قاموس قابل للحفظ.
        """
        usage = payload.get(
            "usage",
            {},
        )

        if usage is None:
            usage = {}

        if not isinstance(
            usage,
            dict,
        ):
            raise ClaudeProcessOutputError(
                "usage must be an object when present."
            )

        metadata = dict(
            usage
        )

        for key in (
            "total_cost_usd",
            "duration_ms",
            "duration_api_ms",
            "is_error",
            "modelUsage",
            "subtype",
            "stop_reason",
        ):
            if key in payload:
                metadata[
                    key
                ] = payload[
                    key
                ]

        return metadata
