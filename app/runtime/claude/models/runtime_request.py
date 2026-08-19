"""
نماذج البيانات التي تصف طلب جلسة Claude ونتيجتها وحالتها.

تمنع هذه النماذج انتقال طلب ناقص أو نتيجة غير قابلة للتفسير إلى بقية رحلة
المراقبة، وتفصل بين المخرجات الخام والنتيجة المنظمة والحالة المحفوظة.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


@dataclass(slots=True, frozen=True)
class ClaudeRuntimeRequest:
    """
    طلب يحدد نوع مهمة Claude وسياقها ووقتها وأدواتها المسموح بها.
    """
    job_id: str
    job_type: str
    prompt: str
    context: dict[str, Any] = field(
        default_factory=dict
    )
    timeout_seconds: float = 60.0
    max_turns: int = 8
    allowed_tools: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        يتحقق من هوية المهمة ونصها وحدودها وأسماء الأدوات قبل السماح بتشغيلها.
        """
        if not self.job_id.strip():
            raise ValueError(
                "job_id must not be empty."
            )

        if not self.job_type.strip():
            raise ValueError(
                "job_type must not be empty."
            )

        if not self.prompt.strip():
            raise ValueError(
                "prompt must not be empty."
            )

        if self.timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be > 0."
            )

        if self.max_turns < 1:
            raise ValueError(
                "max_turns must be >= 1."
            )

        for tool_id in self.allowed_tools:
            if not tool_id.strip():
                raise ValueError(
                    "allowed_tools cannot contain empty IDs."
                )

