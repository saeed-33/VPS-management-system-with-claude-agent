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
from .tool_execution_result import SpecialistLoopToolExecutionResult

class SpecialistLoopToolExecutor:
    """ينفذ طلبات الأدوات بعد تطبيق السياسة ومنع التكرار."""

    def __init__(
        self,
        *,
        diagnostic_policy_engine: DiagnosticPolicyEngine,
        evidence_collection_service: EvidenceCollectionService,
    ) -> None:
        self._diagnostic_policy_engine = diagnostic_policy_engine
        self._evidence_collection_service = evidence_collection_service

    async def execute(
        self,
        *,
        requests: tuple[SpecialistDiagnosticToolRequest, ...],
        round_number: int,
        task: SpecialistTask,
        specialist: SpecialistRuntimeDefinition,
        investigation_budget: InvestigationBudget,
        specialist_actions_used: int,
        investigation_actions_used: int,
        executed_signatures: set[str],
    ) -> SpecialistLoopToolExecutionResult:
        stop_reason = None
        decisions: list[
            SpecialistLoopToolDecision
        ] = []

        round_evidence_ids: list[str] = []
        evidence: list[EvidenceReference] = []

        for requested in requests:
            # يحد النظام عدد الفحوص حتى لا يستمر التحقيق بلا نهاية أو
            # يستهلك متطلبات الحالة كلها في متابع واحد.
            if (
                specialist_actions_used
                >= specialist.max_actions
                or investigation_actions_used
                >= investigation_budget.max_actions
            ):
                decisions.append(
                    SpecialistLoopToolDecision(
                        round_number=(
                            round_number
                        ),
                        tool_id=(
                            requested.call.tool_id
                        ),
                        rationale=(
                            requested.rationale
                        ),
                        decision="skipped",
                        reasons=(
                            "max_actions",
                        ),
                    )
                )
                stop_reason = (
                    SpecialistLoopStopReason
                    .MAX_ACTIONS
                )
                break

            signature = (
                self._request_signature(
                    requested.call
                )
            )

            if (
                signature
                in executed_signatures
            ):
                decisions.append(
                    SpecialistLoopToolDecision(
                        round_number=(
                            round_number
                        ),
                        tool_id=(
                            requested.call.tool_id
                        ),
                        rationale=(
                            requested.rationale
                        ),
                        decision="skipped",
                        reasons=(
                            "duplicate_request",
                        ),
                    )
                )
                continue

            policy = (
                self._diagnostic_policy_engine
                .evaluate(
                    specialist=specialist,
                    request=DiagnosticPolicyRequest(
                        call=requested.call,
                        round_number=(
                            round_number
                        ),
                        specialist_actions_used=(
                            specialist_actions_used
                        ),
                        investigation_actions_used=(
                            investigation_actions_used
                        ),
                        investigation_budget=(
                            investigation_budget
                        ),
                    ),
                )
            )

            if not policy.allowed:
                # لا يكفي أن يطلب النموذج أداة؛ يجب أن تسمح القاعدة بها
                # لحماية السيرفر من فحص غير مقصود.
                decisions.append(
                    SpecialistLoopToolDecision(
                        round_number=(
                            round_number
                        ),
                        tool_id=(
                            requested.call.tool_id
                        ),
                        rationale=(
                            requested.rationale
                        ),
                        decision="denied",
                        reasons=tuple(
                            reason.value
                            for reason
                            in policy.reasons
                        ),
                    )
                )
                continue

            action_number = (
                specialist_actions_used
                + 1
            )

            evidence_id = (
                f"{task.task_id}:"
                f"r{round_number}:"
                f"a{action_number}:"
                f"{policy.tool_id}"
            )

            collected = await (
                self
                ._evidence_collection_service
                .collect(
                    EvidenceCollectionRequest(
                        evidence_id=(
                            evidence_id
                        ),
                        server_id=(
                            task.server_id
                        ),
                        policy_result=policy,
                    )
                )
            )

            # لا يعتمد التحقيق على المعلومة قبل حفظها بمعرف يمكن الرجوع
            # إليه وربطه بالاستنتاج.

            evidence.append(
                collected
            )
            round_evidence_ids.append(
                collected.evidence_id
            )

            specialist_actions_used += 1
            investigation_actions_used += 1

            executed_signatures.add(
                signature
            )

            decisions.append(
                SpecialistLoopToolDecision(
                    round_number=(
                        round_number
                    ),
                    tool_id=(
                        requested.call.tool_id
                    ),
                    rationale=(
                        requested.rationale
                    ),
                    decision="executed",
                    reasons=("allowed",),
                    evidence_id=(
                        collected.evidence_id
                    ),
                )
            )



        return SpecialistLoopToolExecutionResult(
            decisions=tuple(decisions),
            evidence=tuple(evidence),
            evidence_ids=tuple(round_evidence_ids),
            specialist_actions_used=specialist_actions_used,
            investigation_actions_used=investigation_actions_used,
            stop_reason=stop_reason,
        )

    @staticmethod
    def _request_signature(call: DiagnosticToolCall) -> str:
        """ينشئ توقيعًا ثابتًا لطلب أداة لمنع التكرار."""
        normalized_arguments = json.dumps(
            call.arguments,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return call.tool_id.strip().casefold() + ":" + normalized_arguments
