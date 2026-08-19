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

from .rounds_result import SpecialistLoopRoundsResult
from .tool_executor import SpecialistLoopToolExecutor

class SpecialistLoopRoundExecutor:
    """يدير جولات reasoning وجمع الأدلة حتى حد التوقف."""

    def __init__(
        self,
        *,
        context_builder: SpecialistContextBuilder,
        reasoning_agent: SpecialistReasoningAgent,
        tool_executor: SpecialistLoopToolExecutor,
    ) -> None:
        self._context_builder = context_builder
        self._reasoning_agent = reasoning_agent
        self._tool_executor = tool_executor

    async def execute(
        self,
        *,
        task: SpecialistTask,
        specialist: SpecialistRuntimeDefinition,
        investigation_budget: InvestigationBudget,
        tool_catalog: str,
        detected_domains: tuple[str, ...],
        initial_evidence: tuple[EvidenceReference, ...],
        initial_analysis_summary: str | None,
        initial_analysis_issues: tuple[dict, ...],
        incident_contexts,
        allowed_specialist_slugs: tuple[str, ...],
        investigation_actions_used: int,
    ) -> SpecialistLoopRoundsResult:
        evidence = list(initial_evidence)
        traces: list[
            SpecialistLoopRoundTrace
        ] = []

        specialist_actions_used = 0
        global_actions_used = (
            investigation_actions_used
        )

        executed_signatures: set[str] = set()

        effective_round_limit = min(
            specialist.max_rounds,
            investigation_budget.max_rounds,
        )

        catalog = tool_catalog

        final_execution: (
            SpecialistReasoningExecution | None
        ) = None
        remediation_action_suggestions: list[dict] = []
        accumulated_findings: dict[str, InvestigationFinding] = {}

        force_synthesis = False

        stop_reason = (
            SpecialistLoopStopReason.COMPLETED
        )



        for round_number in range(
            1,
            effective_round_limit + 1,
        ):
            # يراجع المتخصص الأدلة المتاحة ثم يطلب فحصًا إضافيًا فقط عندما
            # يحتاج إلى إثبات جديد.
            evidence_ids = tuple(
                dict.fromkeys(
                    task.evidence_ids
                    + tuple(
                        item.evidence_id
                        for item in evidence
                    )
                )
            )

            round_task = replace(
                task,
                evidence_ids=evidence_ids,
                round_number=round_number,
            )

            context = await (
                self._context_builder.build(
                    task=round_task,
                    specialist=specialist,
                    detected_domains=(
                        detected_domains
                    ),
                    evidence=tuple(evidence),
                    initial_analysis_summary=(
                        initial_analysis_summary
                    ),
                    initial_analysis_issues=(
                        initial_analysis_issues
                    ),
                    incident_contexts=(
                        incident_contexts
                    ),
                )
            )

            execution = await (
                self._reasoning_agent.reason(
                    context=context,
                    allowed_specialist_slugs=(
                        allowed_specialist_slugs
                    ),
                    diagnostic_tool_catalog=(
                        None
                        if force_synthesis
                        else catalog
                    ),
                    force_final_synthesis=(
                        force_synthesis
                    ),
                )
            )

            final_execution = execution

            for finding in execution.result.findings:
                accumulated_findings.setdefault(
                    finding.finding_id,
                    finding,
                )

            raw_actions = (execution.result.metadata or {}).get(
                "recommended_remediation_actions", []
            )
            if isinstance(raw_actions, (list, tuple)):
                remediation_action_suggestions.extend(
                    item for item in raw_actions if isinstance(item, dict)
                )

            force_synthesis = False

            requests = (
                execution
                .diagnostic_tool_requests
            )

            if not requests:
                traces.append(
                    SpecialistLoopRoundTrace(
                        round_number=(
                            round_number
                        ),
                        requested_tools=(),
                        collected_evidence_ids=(),
                        tool_decisions=(),
                        confidence=(
                            execution
                            .result
                            .confidence
                        ),
                    )
                )

                stop_reason = (
                    SpecialistLoopStopReason
                    .COMPLETED
                )
                break

            # لا نعد بفحص جديد بعد الجولة الأخيرة؛ نثبت ما جمعناه وننهي التحقيق.
            if (
                round_number
                >= effective_round_limit
            ):
                traces.append(
                    SpecialistLoopRoundTrace(
                        round_number=(
                            round_number
                        ),
                        requested_tools=tuple(
                            item.call.tool_id
                            for item in requests
                        ),
                        collected_evidence_ids=(),
                        tool_decisions=tuple(
                            SpecialistLoopToolDecision(
                                round_number=(
                                    round_number
                                ),
                                tool_id=(
                                    item.call.tool_id
                                ),
                                rationale=(
                                    item.rationale
                                ),
                                decision="skipped",
                                reasons=(
                                    "max_rounds",
                                ),
                            )
                            for item in requests
                        ),
                        confidence=(
                            execution
                            .result
                            .confidence
                        ),
                    )
                )

                stop_reason = (
                    SpecialistLoopStopReason
                    .MAX_ROUNDS
                )
                break

            tool_result = await self._tool_executor.execute(
                requests=tuple(requests),
                round_number=round_number,
                task=task,
                specialist=specialist,
                investigation_budget=investigation_budget,
                specialist_actions_used=specialist_actions_used,
                investigation_actions_used=global_actions_used,
                executed_signatures=executed_signatures,
            )
            decisions = list(tool_result.decisions)
            round_evidence_ids = list(tool_result.evidence_ids)
            evidence.extend(tool_result.evidence)
            specialist_actions_used = tool_result.specialist_actions_used
            global_actions_used = tool_result.investigation_actions_used
            if tool_result.stop_reason is not None:
                stop_reason = tool_result.stop_reason

            traces.append(
                SpecialistLoopRoundTrace(
                    round_number=(
                        round_number
                    ),
                    requested_tools=tuple(
                        item.call.tool_id
                        for item in requests
                    ),
                    collected_evidence_ids=(
                        tuple(
                            round_evidence_ids
                        )
                    ),
                    tool_decisions=tuple(
                        decisions
                    ),
                    confidence=(
                        execution
                        .result
                        .confidence
                    ),
                )
            )

            if (
                stop_reason
                == SpecialistLoopStopReason
                .MAX_ACTIONS
            ):
                break

            if not round_evidence_ids:
                if (
                    round_number
                    < effective_round_limit
                ):
                    force_synthesis = True
                    continue

                stop_reason = (
                    SpecialistLoopStopReason
                    .NO_EVIDENCE_COLLECTED
                )
                break



        return SpecialistLoopRoundsResult(
            final_execution=final_execution,
            evidence=tuple(evidence),
            traces=tuple(traces),
            specialist_actions_used=specialist_actions_used,
            investigation_actions_used=global_actions_used,
            stop_reason=stop_reason,
            remediation_action_suggestions=tuple(remediation_action_suggestions),
            accumulated_findings=dict(accumulated_findings),
        )
