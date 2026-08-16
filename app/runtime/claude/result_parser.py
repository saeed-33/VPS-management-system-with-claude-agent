"""
تحويل النص النهائي من Claude إلى نتيجة تشغيل منظمة.

يزيل غلاف Markdown عند وجوده، يفك JSON، ويتحقق من الحالة والملخص والبيانات قبل
أن تسمح الخدمة باعتبار الجلسة مكتملة أو فاشلة.
"""
from __future__ import annotations

import json
from typing import Any

from app.runtime.claude.exceptions import (
    ClaudeStructuredOutputError,
)
from app.runtime.claude.models import (
    ClaudeJobStatus,
    ClaudeStructuredOutput,
)


def _strip_code_fence(
    content: str,
) -> str:
    """
    يزيل غلاف Markdown من النص عندما تعيد الجلسة JSON داخل كتلة كود.
    """
    cleaned = content.strip()

    if not cleaned.startswith("```"):
        return cleaned

    lines = cleaned.splitlines()

    if lines and lines[0].strip().lower() in {
        "```",
        "```json",
    }:
        lines = lines[1:]

    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()


class ClaudeStructuredResultParser:
    """
    محلل يتحقق من JSON النهائي ويحوّله إلى نتيجة تشغيل ذات حالة واضحة.
    """
    def parse(
        self,
        content: str,
    ) -> ClaudeStructuredOutput:
        """
        يفك JSON النهائي ويتحقق من أنه كائن ثم يمرره إلى تحويل النتيجة المنظمة.
        """
        cleaned = _strip_code_fence(
            content
        )

        try:
            decoded = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ClaudeStructuredOutputError(
                "Claude returned invalid JSON."
            ) from exc

        if not isinstance(decoded, dict):
            raise ClaudeStructuredOutputError(
                "Claude structured output must be an object."
            )

        return self._parse_object(
            decoded
        )

    def _parse_object(
        self,
        decoded: dict[str, Any],
    ) -> ClaudeStructuredOutput:
        """
        يتحقق من الحالة والملخص والبيانات والبيانات الوصفية وينشئ مخرجًا منظمًا.
        """
        raw_status = decoded.get("status")

        if not isinstance(raw_status, str):
            raise ClaudeStructuredOutputError(
                "Claude structured output is missing status."
            )

        try:
            status = ClaudeJobStatus(raw_status)
        except ValueError as exc:
            raise ClaudeStructuredOutputError(
                f"Unsupported Claude status: {raw_status!r}."
            ) from exc

        summary = decoded.get("summary")

        if not isinstance(summary, str):
            raise ClaudeStructuredOutputError(
                "Claude structured output is missing summary."
            )

        data = decoded.get("data", {})

        if not isinstance(data, dict):
            raise ClaudeStructuredOutputError(
                "Claude structured output data must be an object."
            )

        metadata = decoded.get("metadata", {})

        if not isinstance(metadata, dict):
            raise ClaudeStructuredOutputError(
                "Claude structured output metadata must be an object."
            )

        try:
            return ClaudeStructuredOutput(
                status=status,
                summary=summary,
                data=data,
                metadata=metadata,
            )
        except ValueError as exc:
            raise ClaudeStructuredOutputError(
                str(exc)
            ) from exc
