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

from app.core.contracts.investigation.evidence_collection_request import EvidenceCollectionRequest
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

from .finalizer import SpecialistLoopFinalizer
from .round_executor import SpecialistLoopRoundExecutor
from .tool_executor import SpecialistLoopToolExecutor

class SpecialistInvestigationLoop:
    """
    يدير جولات الاختصاصي وحدود الأدوات وسبب التوقف.
    """

    def __init__(
        self,
        *,
        context_builder: SpecialistContextBuilder,
        reasoning_agent: SpecialistReasoningAgent,
        diagnostic_tool_registry: DiagnosticToolRegistry,
        diagnostic_policy_engine: DiagnosticPolicyEngine,
        evidence_collection_service: EvidenceCollectionService,
    ) -> None:
        self._diagnostic_tool_registry = diagnostic_tool_registry
        tool_executor = SpecialistLoopToolExecutor(
            diagnostic_policy_engine=diagnostic_policy_engine,
            evidence_collection_service=evidence_collection_service,
        )
        self._round_executor = SpecialistLoopRoundExecutor(
            context_builder=context_builder,
            reasoning_agent=reasoning_agent,
            tool_executor=tool_executor,
        )
        self._finalizer = SpecialistLoopFinalizer(
            context_builder=context_builder,
            reasoning_agent=reasoning_agent,
        )

    async def run(
        self,
        *,
        task: SpecialistTask,
        specialist: SpecialistRuntimeDefinition,
        investigation_budget: InvestigationBudget,
        detected_domains: tuple[str, ...] = (),
        initial_evidence: tuple[EvidenceReference, ...] = (),
        initial_analysis_summary: str | None = None,
        initial_analysis_issues: tuple[dict, ...] = (),
        incident_contexts=(),
        allowed_specialist_slugs: tuple[str, ...] = (),
        investigation_actions_used: int = 0,
    ) -> SpecialistInvestigationLoopResult:
        """يدير جولات reasoning واستدعاء الأدوات حتى نتيجة أو حد توقف."""
        if task.specialist_id.strip().casefold() != specialist.slug:
            raise ValueError(
                "Task specialist does not match Specialist definition."
            )
        if investigation_actions_used < 0:
            raise ValueError("investigation_actions_used must be >= 0.")

        tool_catalog = self._render_tool_catalog(specialist)
        rounds = await self._round_executor.execute(
            task=task,
            specialist=specialist,
            investigation_budget=investigation_budget,
            tool_catalog=tool_catalog,
            detected_domains=detected_domains,
            initial_evidence=initial_evidence,
            initial_analysis_summary=initial_analysis_summary,
            initial_analysis_issues=initial_analysis_issues,
            incident_contexts=incident_contexts,
            allowed_specialist_slugs=allowed_specialist_slugs,
            investigation_actions_used=investigation_actions_used,
        )
        return await self._finalizer.finalize(
            rounds=rounds,
            task=task,
            specialist=specialist,
            investigation_budget=investigation_budget,
            detected_domains=detected_domains,
            initial_analysis_summary=initial_analysis_summary,
            initial_analysis_issues=initial_analysis_issues,
            incident_contexts=incident_contexts,
            allowed_specialist_slugs=allowed_specialist_slugs,
        )


    def _render_tool_catalog(
        self,
        specialist: SpecialistRuntimeDefinition,
    ) -> str:
        """
        ينشئ كتالوج الأدوات المتاحة للاختصاصي.
        """
        entries: list[dict] = []

        for tool_id in (
            specialist.allowed_tool_ids
        ):
            definition = (
                self
                ._diagnostic_tool_registry
                .get(tool_id)
            )

            if definition is None:
                continue

            entries.append(
                {
                    "tool_id": (
                        definition.tool_id
                    ),
                    "name": definition.name,
                    "description": (
                        definition.description
                    ),
                    "domains": list(
                        definition.domains
                    ),
                    "parameters": [
                        {
                            "name": (
                                parameter.name
                            ),
                            "kind": (
                                parameter.kind.value
                            ),
                            "required": (
                                parameter.required
                            ),
                            "default": (
                                parameter.default
                            ),
                            "minimum": (
                                parameter.minimum
                            ),
                            "maximum": (
                                parameter.maximum
                            ),
                            "description": (
                                parameter.description
                            ),
                        }
                        for parameter
                        in definition.parameters
                    ],
                }
            )

        if not entries:
            return (
                "No diagnostic tools are "
                "assigned to this Specialist."
            )

        return json.dumps(
            entries,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )



    @staticmethod
    def _request_signature(call: DiagnosticToolCall) -> str:
        """يحافظ على واجهة توقيع الطلب القديمة."""
        return SpecialistLoopToolExecutor._request_signature(call)

    @staticmethod
    def _ensure_evidence_backed_finding(**kwargs) -> SpecialistResult:
        """يحافظ على واجهة إنشاء finding القديمة."""
        return SpecialistLoopFinalizer._ensure_evidence_backed_finding(**kwargs)
