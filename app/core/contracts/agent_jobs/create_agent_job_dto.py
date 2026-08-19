"""Contract class extracted from agent_jobs.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from typing import Any

@dataclass(slots=True, frozen=True)
class CreateAgentJobDTO:
    """
    البيانات اللازمة لفتح سجل مهمة قبل بدء جلسة التنفيذ.

    يربط العقد المهمة بنوعها والسيرفر وسياقها حتى يمكن تتبعها من الانتظار
    إلى النتيجة النهائية.
    """
    job_id: str
    job_type: str
    status: str
    server_id: int | None = None
    claude_session_id: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """يتحقق من هوية المهمة وحالتها ومعرف السيرفر قبل حفظها."""
        if not self.job_id.strip():
            raise ValueError(
                "job_id must not be empty."
            )

        if not self.job_type.strip():
            raise ValueError(
                "job_type must not be empty."
            )

        if not self.status.strip():
            raise ValueError(
                "status must not be empty."
            )

        if (
            self.server_id is not None
            and self.server_id < 1
        ):
            raise ValueError(
                "server_id must be >= 1 when provided."
            )
