"""Class extracted from correlation during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import re

from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.investigation_finding import InvestigationFinding
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus

from app.capabilities.investigation.execution_contracts.investigation_execution_result import InvestigationExecutionResult

from .diagnosis_certainty import DiagnosisCertainty

@dataclass(slots=True, frozen=True)
class CorrelatedDiagnosisClaim:
    """
    يمثل ادعاء تشخيصي بعد ربطه بمصادر وأدلة الاختصاصيين.
    """
    claim_id: str
    title: str
    description: str
    certainty: DiagnosisCertainty
    confidence: float
    specialist_slugs: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    knowledge_source_ids: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    metadata: dict | None = None

    def __post_init__(self) -> None:
        """
        يتحقق من صحة بيانات CorrelatedDiagnosisClaim قبل استخدامها في التحقيق.
        """
        if not self.claim_id.strip():
            raise ValueError(
                "claim_id must not be empty."
            )
        if not self.title.strip():
            raise ValueError(
                "Claim title must not be empty."
            )
        if not self.description.strip():
            raise ValueError(
                "Claim description must not be empty."
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Claim confidence must be between 0 and 1."
            )
        if self.metadata is None:
            object.__setattr__(
                self,
                "metadata",
                {},
            )
