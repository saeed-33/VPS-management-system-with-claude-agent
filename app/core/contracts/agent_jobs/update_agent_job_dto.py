"""Contract class extracted from agent_jobs.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from typing import Any

@dataclass(slots=True, frozen=True)
class UpdateAgentJobDTO:
    """
    القيم التي تغير حالة مهمة موجودة وتصف نتيجة تنفيذها.

    يحمل العقد معرف الجلسة ووقت الاكتمال وسبب الفشل وعداد الجولات والأدوات،
    حتى يبقى أثر التنفيذ كاملًا عند عرضه أو مراجعته.
    """
    status: str
    claude_session_id: str | None = None
    completed_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None
    turn_count: int = 0
    tool_call_count: int = 0
    usage_metadata: dict[str, Any] = field(
        default_factory=dict
    )
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """يتحقق من حالة التحديث ومن عدم سلبية عدادات الجلسة."""
        if not self.status.strip():
            raise ValueError(
                "status must not be empty."
            )

        if self.turn_count < 0:
            raise ValueError(
                "turn_count must be >= 0."
            )

        if self.tool_call_count < 0:
            raise ValueError(
                "tool_call_count must be >= 0."
            )
