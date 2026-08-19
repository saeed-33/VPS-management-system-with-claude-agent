"""
قراءة مخرجات Claude بصيغة JSON المفردة أو stream-json.

تستخرج معرف الجلسة والنتيجة والعدادات والأدوات وخوادم MCP، وترفض الجلسة التي
لا تثبت اتصال أداة VPS وتنفيذ الفحوص التشغيلية المطلوبة.
"""
from __future__ import annotations

import json

from app.runtime.claude.exceptions.process_output_error import ClaudeProcessOutputError
from app.runtime.claude.models.raw_result import ClaudeRawResult


class _ClaudeCliJsonDecoderMixin3:
    """ينظم مجموعة من عمليات المكون."""

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
