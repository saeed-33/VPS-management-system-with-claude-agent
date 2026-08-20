"""Class extracted from specialist_reasoning_agent during the structure refactor."""

from __future__ import annotations

import re

from dataclasses import dataclass

from app.core.contracts.investigation.investigation_finding import InvestigationFinding
from app.core.contracts.investigation.investigation_hypothesis import InvestigationHypothesis
from app.core.contracts.investigation.specialist_result import SpecialistResult
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus

from app.core.policies.diagnostic_tools.diagnostic_tool_call import DiagnosticToolCall

from app.capabilities.investigation.specialist_context.specialist_context_snapshot import SpecialistContextSnapshot

from app.core.contracts.specialist_reasoning.specialist_reasoning_client import (
    SpecialistReasoningClient,
)

from app.core.contracts.specialist_reasoning.specialist_reasoning_output import SpecialistReasoningOutput

from app.core.policies.remediation_tools.constants import SERVICE_NAME_RE

from app.capabilities.investigation.source_location import extract_source_locations

from .specialist_diagnostic_tool_request import SpecialistDiagnosticToolRequest

@dataclass(slots=True, frozen=True)
class SpecialistReasoningExecution:
    """
    يمثل استجابة reasoning الاختصاصي مع الادعاءات والتوصيات والمراجع.
    """
    result: SpecialistResult
    provider: str
    model: str
    diagnostic_tool_requests: tuple[
        SpecialistDiagnosticToolRequest,
        ...
    ] = ()
