"""Class extracted from execution_contracts during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.contracts.investigation.server_investigation_state import ServerInvestigationState
from app.core.contracts.investigation.specialist_result import SpecialistResult
from app.core.contracts.investigation.specialist_task import SpecialistTask

from app.capabilities.investigation.specialist_investigation_loop.specialist_investigation_loop_result import SpecialistInvestigationLoopResult

@dataclass(slots=True, frozen=True)
class InvestigationSpecialistRun:
    """
    يمثل سجل تشغيل اختصاصي داخل التحقيق.
    """
    specialist_slug: str
    task: SpecialistTask
    result: SpecialistResult
    loop_result: SpecialistInvestigationLoopResult | None
