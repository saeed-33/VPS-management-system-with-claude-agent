"""Class extracted from specialist_investigation_loop during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, replace

from enum import StrEnum

import json

from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.investigation_budget import InvestigationBudget
from app.core.contracts.investigation.investigation_finding import InvestigationFinding
from app.core.contracts.investigation.specialist_result import SpecialistResult
from app.core.contracts.investigation.specialist_task import SpecialistTask

from app.core.policies.diagnostic_policy.diagnostic_policy_engine import DiagnosticPolicyEngine
from app.core.policies.diagnostic_policy.diagnostic_policy_request import DiagnosticPolicyRequest

from app.core.policies.diagnostic_tools.diagnostic_tool_call import DiagnosticToolCall
from app.core.policies.diagnostic_tools.diagnostic_tool_registry import DiagnosticToolRegistry

from app.capabilities.investigation.evidence_collection.evidence_collection_request import EvidenceCollectionRequest
from app.capabilities.investigation.evidence_collection.evidence_collection_service import EvidenceCollectionService

from app.capabilities.investigation.specialist_context.specialist_context_builder import SpecialistContextBuilder

from app.capabilities.investigation.specialist_reasoning_agent.specialist_diagnostic_tool_request import SpecialistDiagnosticToolRequest
from app.capabilities.investigation.specialist_reasoning_agent.specialist_reasoning_agent import SpecialistReasoningAgent
from app.capabilities.investigation.specialist_reasoning_agent.specialist_reasoning_execution import SpecialistReasoningExecution

from app.capabilities.investigation.specialist_registry.specialist_runtime_definition import SpecialistRuntimeDefinition

from .specialist_investigation_loop_result import SpecialistInvestigationLoopResult

from .specialist_loop_round_trace import SpecialistLoopRoundTrace

from .specialist_loop_stop_reason import SpecialistLoopStopReason

from .specialist_loop_tool_decision import SpecialistLoopToolDecision

from .specialist_loop_round_trace import SpecialistLoopRoundTrace
from .specialist_loop_stop_reason import SpecialistLoopStopReason

@dataclass(slots=True, frozen=True)
class SpecialistLoopRoundsResult:
    final_execution: SpecialistReasoningExecution | None
    evidence: tuple[EvidenceReference, ...]
    traces: tuple[SpecialistLoopRoundTrace, ...]
    specialist_actions_used: int
    investigation_actions_used: int
    stop_reason: SpecialistLoopStopReason
    remediation_action_suggestions: tuple[dict, ...]
    accumulated_findings: dict[str, InvestigationFinding]
