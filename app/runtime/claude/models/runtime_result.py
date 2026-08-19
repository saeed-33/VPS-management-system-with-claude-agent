"""
نماذج البيانات التي تصف طلب جلسة Claude ونتيجتها وحالتها.

تمنع هذه النماذج انتقال طلب ناقص أو نتيجة غير قابلة للتفسير إلى بقية رحلة
المراقبة، وتفصل بين المخرجات الخام والنتيجة المنظمة والحالة المحفوظة.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from .job_status import ClaudeJobStatus
from .structured_output import ClaudeStructuredOutput


@dataclass(slots=True, frozen=True)
class ClaudeRuntimeResult:
    """
    النتيجة النهائية القابلة للحفظ لمهمة Claude، بما فيها الفشل أو المهلة ومؤشرات الاستخدام.
    """
    job_id: str
    job_type: str
    status: ClaudeJobStatus
    session_id: str | None = None
    structured_output: ClaudeStructuredOutput | None = None
    error_code: str | None = None
    error_message: str | None = None
    turn_count: int = 0
    tool_call_count: int = 0
    usage_metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        يتحقق من هوية المهمة ونوعها وعدادات النتيجة النهائية قبل تسجيلها.
        """
        if not self.job_id.strip():
            raise ValueError(
                "job_id must not be empty."
            )

        if not self.job_type.strip():
            raise ValueError(
                "job_type must not be empty."
            )

        if self.turn_count < 0:
            raise ValueError(
                "turn_count must be >= 0."
            )

        if self.tool_call_count < 0:
            raise ValueError(
                "tool_call_count must be >= 0."
            )

