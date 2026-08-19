"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

from .specialist_task_status import SpecialistTaskStatus

@dataclass(slots=True, frozen=True)
class SpecialistTask:
    """
    طلب تحقيق موجه إلى متخصص حول سيرفر وتقرير وهدف محدد.

    يربط العقد المهمة بجولة التحقيق والأدلة المتاحة والميزانية حتى لا يعمل
    المتخصص خارج الحالة التي طلبته.
    """
    task_id: str
    investigation_id: str
    server_id: int
    report_id: int
    specialist_id: str
    objective: str
    trigger_issue_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    knowledge_topics: tuple[str, ...] = ()
    round_number: int = 1
    status: SpecialistTaskStatus = (
        SpecialistTaskStatus.PENDING
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """يتحقق من ارتباط المهمة بالتحقيق والسيرفر والتقرير ومن صحة الجولة."""
        if not self.task_id.strip():
            raise ValueError(
                "task_id must not be empty."
            )
        if not self.investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )
        if self.server_id < 1:
            raise ValueError(
                "server_id must be >= 1."
            )
        if self.report_id < 1:
            raise ValueError(
                "report_id must be >= 1."
            )
        if not self.specialist_id.strip():
            raise ValueError(
                "specialist_id must not be empty."
            )
        if not self.objective.strip():
            raise ValueError(
                "Specialist objective must not be empty."
            )
        if self.round_number < 1:
            raise ValueError(
                "round_number must be >= 1."
            )
