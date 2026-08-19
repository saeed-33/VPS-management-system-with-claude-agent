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
class ClaudeRawResult:
    """
    المخرج الخام الذي تعيده الجلسة مع معرفها وعدد جولاتها وأدواتها.
    """
    session_id: str
    content: str
    turn_count: int = 0
    tool_call_count: int = 0
    usage_metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        يتحقق من وجود معرف ومحتوى للجلسة ومن عدم سلبية عداداتها.
        """
        if not self.session_id.strip():
            raise ValueError(
                "session_id must not be empty."
            )

        if not self.content.strip():
            raise ValueError(
                "content must not be empty."
            )

        if self.turn_count < 0:
            raise ValueError(
                "turn_count must be >= 0."
            )

        if self.tool_call_count < 0:
            raise ValueError(
                "tool_call_count must be >= 0."
            )

