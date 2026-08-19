"""Class extracted from correlation during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import re

from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.investigation_finding import InvestigationFinding
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus

from app.capabilities.investigation.execution_contracts.investigation_execution_result import InvestigationExecutionResult

from .correlated_diagnosis_claim import CorrelatedDiagnosisClaim

from .diagnosis_conflict import DiagnosisConflict

@dataclass(slots=True, frozen=True)
class FinalDiagnosis:
    """
    يمثل التشخيص النهائي المجمع مع الادعاءات والتعارضات ومواقع المصادر.
    """
    investigation_id: str
    summary: str
    claims: tuple[
        CorrelatedDiagnosisClaim,
        ...
    ]
    conflicts: tuple[
        DiagnosisConflict,
        ...
    ]
    confirmed_count: int
    probable_count: int
    unknown_count: int
    conflict_count: int
    evidence_ids: tuple[str, ...]
    specialist_slugs: tuple[str, ...]
    metadata: dict

    def __post_init__(self) -> None:
        """
        يتحقق من صحة بيانات FinalDiagnosis قبل استخدامها في التحقيق.
        """
        if not self.investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )
        if not self.summary.strip():
            raise ValueError(
                "Final diagnosis summary must not be empty."
            )
        if self.conflict_count != len(
            self.conflicts
        ):
            raise ValueError(
                "conflict_count must match conflicts."
            )
