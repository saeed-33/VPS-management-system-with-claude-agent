from __future__ import annotations

from dataclasses import dataclass

from app.domain.investigation.contracts import (
    ServerInvestigationState,
    SpecialistResult,
    SpecialistTask,
)
from app.domain.investigation.specialist_investigation_loop import (
    SpecialistInvestigationLoopResult,
)


@dataclass(slots=True, frozen=True)
class InvestigationSpecialistRun:
    specialist_slug: str
    task: SpecialistTask
    result: SpecialistResult
    loop_result: SpecialistInvestigationLoopResult | None


@dataclass(slots=True, frozen=True)
class InvestigationExecutionResult:
    state: ServerInvestigationState
    runs: tuple[InvestigationSpecialistRun, ...]
    investigation_actions_used: int
