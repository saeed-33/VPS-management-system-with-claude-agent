"""Class extracted from correlation during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import re

from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.investigation_finding import InvestigationFinding
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus

from app.capabilities.investigation.execution_contracts.investigation_execution_result import InvestigationExecutionResult

class DiagnosisCertainty(StrEnum):
    """
    يمثل درجات اليقين الممكنة في ادعاء التشخيص النهائي.
    """
    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    UNKNOWN = "unknown"
