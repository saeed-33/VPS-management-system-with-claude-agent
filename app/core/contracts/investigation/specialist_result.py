"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

from .investigation_finding import InvestigationFinding

from .investigation_hypothesis import InvestigationHypothesis

from .specialist_task_status import SpecialistTaskStatus

@dataclass(slots=True, frozen=True)
class SpecialistResult:
    """
    النتيجة النهائية لمهمة متخصص مع ملخص ونتائج وفرضيات وأدلة ناقصة.

    لا يسمح العقد بحفظ نتيجة ما زالت معلقة، ويجعل مستوى الثقة والمراجع جزءًا من
    المادة التي سيستخدمها التجميع النهائي للتشخيص.
    """
    task_id: str
    specialist_id: str
    status: SpecialistTaskStatus
    summary: str
    confidence: float
    findings: tuple[InvestigationFinding, ...] = ()
    hypotheses: tuple[
        InvestigationHypothesis,
        ...
    ] = ()
    ruled_out: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    knowledge_source_ids: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    recommended_next_specialists: tuple[
        str,
        ...
    ] = ()
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """يتحقق من هوية المهمة والمتخصص وملخص النتيجة وحالتها وثقتها."""
        if not self.task_id.strip():
            raise ValueError(
                "task_id must not be empty."
            )
        if not self.specialist_id.strip():
            raise ValueError(
                "specialist_id must not be empty."
            )
        if not self.summary.strip():
            raise ValueError(
                "Specialist summary must not be empty."
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Specialist confidence must be between 0 and 1."
            )

        if self.status == SpecialistTaskStatus.PENDING:
            raise ValueError(
                "SpecialistResult cannot have pending status."
            )
