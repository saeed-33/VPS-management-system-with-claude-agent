"""
قراءة مخرجات Claude بصيغة JSON المفردة أو stream-json.

تستخرج معرف الجلسة والنتيجة والعدادات والأدوات وخوادم MCP، وترفض الجلسة التي
لا تثبت اتصال أداة VPS وتنفيذ الفحوص التشغيلية المطلوبة.
"""
from __future__ import annotations

import json

from app.runtime.claude.exceptions.process_output_error import ClaudeProcessOutputError
from app.runtime.claude.models.raw_result import ClaudeRawResult


class _ContentExtractorMixin:
    """ينظم مجموعة من عمليات المكون."""

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
