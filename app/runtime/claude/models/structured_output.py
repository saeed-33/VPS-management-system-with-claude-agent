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


@dataclass(slots=True, frozen=True)
class ClaudeStructuredOutput:
    """
    النتيجة التي فكها النظام من مخرج Claude وتحتوي الحالة والملخص والبيانات.
    """
    status: ClaudeJobStatus
    summary: str
    data: dict[str, Any] = field(
        default_factory=dict
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        يتأكد أن النتيجة تحمل حالة نهائية وملخصًا يمكن حفظه وعرضه.
        """
        if self.status not in {
            ClaudeJobStatus.COMPLETED,
            ClaudeJobStatus.FAILED,
            ClaudeJobStatus.CANCELLED,
        }:
            raise ValueError(
                "structured status must be completed, "
                "failed, or cancelled."
            )

        if not self.summary.strip():
            raise ValueError(
                "summary must not be empty."
            )

