"""
جزء من Claude Runtime لبناء العملية أو تشغيل الجلسة أو قراءة stream أو تسجيل job.

الموقع في المعمارية: Claude supervisory runtime.
يُستدعى بواسطة: composition أو Scheduler.
يعتمد مباشرة على: app.runtime.claude.exceptions، app.runtime.claude.models.
الحد المعماري: Claude/Ollama للـreasoning/model؛ policy والحفظ والتنفيذ الحتمي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

    تُستدعى عندما يصل workflow إلى _strip_code_fence؛ المدخلات المهمة: content.
    تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يمثل ClaudeStructuredResultParser مسؤولية محددة داخل طبقة Claude supervisory runtime.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه composition أو Scheduler
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def parse(
        self,
        content: str,
    ) -> ClaudeStructuredOutput:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى parse؛ المدخلات المهمة: content.
        تعيد ClaudeStructuredOutput أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى _parse_object؛ المدخلات المهمة: decoded.
        تعيد ClaudeStructuredOutput أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
