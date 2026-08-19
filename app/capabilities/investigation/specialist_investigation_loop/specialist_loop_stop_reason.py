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

class SpecialistLoopStopReason(StrEnum):
    """
    يمثل سبب توقف حلقة الاختصاصي.
    """
    COMPLETED = "completed"
    MAX_ROUNDS = "max_rounds"
    MAX_ACTIONS = "max_actions"
    NO_EVIDENCE_COLLECTED = "no_evidence_collected"
