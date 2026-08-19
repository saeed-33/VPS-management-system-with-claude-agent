"""
قراءة مخرجات Claude بصيغة JSON المفردة أو stream-json.

تستخرج معرف الجلسة والنتيجة والعدادات والأدوات وخوادم MCP، وترفض الجلسة التي
لا تثبت اتصال أداة VPS وتنفيذ الفحوص التشغيلية المطلوبة.
"""
from __future__ import annotations

import json

from app.runtime.claude.exceptions.process_output_error import ClaudeProcessOutputError
from app.runtime.claude.models.raw_result import ClaudeRawResult


class _EnvelopeDecoderMixin:
    """ينظم مجموعة من عمليات المكون."""

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
