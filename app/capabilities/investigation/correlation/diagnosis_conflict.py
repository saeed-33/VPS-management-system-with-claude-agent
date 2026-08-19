"""Class extracted from correlation during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import re

from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.investigation_finding import InvestigationFinding
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus

from app.capabilities.investigation.execution_contracts.investigation_execution_result import InvestigationExecutionResult

@dataclass(slots=True, frozen=True)
class DiagnosisConflict:
    """
    يمثل تعارضًا بين نتائج اختصاصيين حول الحقل أو السبب أو الدليل.
    """
    conflict_id: str
    title: str
    diagnostic_states: tuple[str, ...]
    specialist_slugs: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    source_finding_ids: tuple[str, ...]
    description: str

    def __post_init__(self) -> None:
        """
        يتحقق من صحة بيانات DiagnosisConflict قبل استخدامها في التحقيق.
        """
        if not self.conflict_id.strip():
            raise ValueError(
                "conflict_id must not be empty."
            )
        if not self.title.strip():
            raise ValueError(
                "Conflict title must not be empty."
            )
        if len(self.diagnostic_states) < 2:
            raise ValueError(
                "A conflict requires at least two states."
            )
