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

from .rounds_result import SpecialistLoopRoundsResult

class SpecialistLoopFinalizer:
    """ينفذ التلخيص النهائي ويحافظ على الأدلة والنتائج السابقة."""

    def __init__(
        self,
        *,
        context_builder: SpecialistContextBuilder,
        reasoning_agent: SpecialistReasoningAgent,
    ) -> None:
        self._context_builder = context_builder
        self._reasoning_agent = reasoning_agent

    async def finalize(
        self,
        *,
        rounds: SpecialistLoopRoundsResult,
        task: SpecialistTask,
        specialist: SpecialistRuntimeDefinition,
        investigation_budget: InvestigationBudget,
        detected_domains: tuple[str, ...],
        initial_analysis_summary: str | None,
        initial_analysis_issues: tuple[dict, ...],
        incident_contexts,
        allowed_specialist_slugs: tuple[str, ...],
    ) -> SpecialistInvestigationLoopResult:
        final_execution = rounds.final_execution
        evidence = list(rounds.evidence)
        traces = rounds.traces
        stop_reason = rounds.stop_reason
        accumulated_findings = rounds.accumulated_findings
        remediation_action_suggestions = rounds.remediation_action_suggestions
        specialist_actions_used = rounds.specialist_actions_used
        global_actions_used = rounds.investigation_actions_used
        effective_round_limit = min(
            specialist.max_rounds,
            investigation_budget.max_rounds,
        )

        if final_execution is None:
            raise RuntimeError(
                "Specialist loop produced no reasoning result."
            )

        # عند بلوغ الحد، نلخص الأدلة المتاحة بدل ترك التحقيق مع طلب فحص لم ينفذ.
        if stop_reason in (
            SpecialistLoopStopReason.MAX_ROUNDS,
            SpecialistLoopStopReason.MAX_ACTIONS,
        ):
            # الملخص النهائي لا يفتح جولة جديدة ولا ينفذ فحصًا بعد نفاد الحدود.
            synthesis_evidence_ids = tuple(
                dict.fromkeys(
                    task.evidence_ids
                    + tuple(
                        item.evidence_id
                        for item in evidence
                    )
                )
            )

            synthesis_task = replace(
                task,
                evidence_ids=synthesis_evidence_ids,
                round_number=max(
                    1,
                    effective_round_limit,
                ),
            )

            synthesis_context = await (
                self._context_builder.build(
                    task=synthesis_task,
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

            final_execution = await (
                self._reasoning_agent.reason(
                    context=synthesis_context,
                    allowed_specialist_slugs=(
                        allowed_specialist_slugs
                    ),
                    diagnostic_tool_catalog=None,
                    force_final_synthesis=True,
                )
            )

        final_result = final_execution.result
        if not final_result.findings and accumulated_findings:
            historical_evidence_ids = tuple(
                dict.fromkeys(
                    final_result.evidence_ids
                    + tuple(
                        evidence_id
                        for finding in accumulated_findings.values()
                        for evidence_id in finding.evidence_ids
                    )
                )
            )
            final_result = replace(
                final_result,
                findings=tuple(accumulated_findings.values()),
                evidence_ids=historical_evidence_ids,
                metadata={
                    **dict(final_result.metadata or {}),
                    "findings_preserved_from_previous_round": True,
                },
            )

        final_result = self._ensure_evidence_backed_finding(
            result=final_result,
            evidence=tuple(evidence),
        )

        # قد تنتهي الحلقة بتلخيص نهائي لا يعيد اقتراحات الجولة السابقة؛ نحافظ
        # على الاقتراحات المنظمة كي تصل إلى مرحلة إنشاء الخطة دون فقدها.
        final_result = replace(
            final_result,
            metadata={
                **dict(final_result.metadata or {}),
                "recommended_remediation_actions": (
                    remediation_action_suggestions
                ),
            },
        )

        return SpecialistInvestigationLoopResult(
            final_result=(
                final_result
            ),
            evidence=tuple(evidence),
            rounds_completed=len(traces),
            actions_executed=(
                specialist_actions_used
            ),
            investigation_actions_used=(
                global_actions_used
            ),
            stop_reason=stop_reason,
            provider=(
                final_execution.provider
            ),
            model=final_execution.model,
            traces=tuple(traces),
        )



    @staticmethod
    def _ensure_evidence_backed_finding(
        *,
        result: SpecialistResult,
        evidence: tuple[EvidenceReference, ...],
    ) -> SpecialistResult:
        """
        يحول الخلاصة عالية الثقة إلى نتيجة منظمة عند غياب finding من النموذج.

        لا ينشئ هذا المسار دليلاً جديداً؛ يربط نص الخلاصة بالأدلة التي جمعتها
        الحلقة فعلياً، ولا يعمل عند وجود أدلة ناقصة أو ثقة منخفضة.
        """
        if (
            result.findings
            or not evidence
            or result.confidence < 0.8
            or result.missing_evidence
        ):
            return result

        evidence_ids = tuple(
            dict.fromkeys(item.evidence_id for item in evidence)
        )
        finding = InvestigationFinding(
            finding_id=f"{result.task_id}:finding:summary",
            title=(
                f"{result.specialist_id} evidence-backed conclusion"
            ),
            description=result.summary,
            confidence=result.confidence,
            evidence_ids=evidence_ids,
            metadata={
                "derived_from_specialist_summary": True,
                "evidence_count": len(evidence_ids),
            },
        )
        return replace(
            result,
            findings=(finding,),
            evidence_ids=evidence_ids,
            metadata={
                **dict(result.metadata or {}),
                "finding_derived_from_summary": True,
            },
        )
