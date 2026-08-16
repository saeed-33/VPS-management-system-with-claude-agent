"""
إدارة حلقات تنفيذ أدوات الاختصاصي.

تشغل جولات reasoning محدودة، تفسر طلبات الأدوات، تتبع التقدم، وتوقف الحلقة
عند الوصول إلى نتيجة أو حد آمن.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
import json

from app.core.contracts.investigation import (
    EvidenceReference,
    InvestigationBudget,
    SpecialistResult,
    SpecialistTask,
)
from app.core.policies.diagnostic_policy import (
    DiagnosticPolicyEngine,
    DiagnosticPolicyRequest,
)
from app.core.policies.diagnostic_tools import (
    DiagnosticToolCall,
    DiagnosticToolRegistry,
)
from app.capabilities.investigation.evidence_collection import (
    EvidenceCollectionRequest,
    EvidenceCollectionService,
)
from app.capabilities.investigation.specialist_context import (
    SpecialistContextBuilder,
)
from app.capabilities.investigation.specialist_reasoning_agent import (
    SpecialistDiagnosticToolRequest,
    SpecialistReasoningAgent,
    SpecialistReasoningExecution,
)
from app.capabilities.investigation.specialist_registry import (
    SpecialistRuntimeDefinition,
)


class SpecialistLoopStopReason(StrEnum):
    """
    يمثل سبب توقف حلقة الاختصاصي.
    """
    COMPLETED = "completed"
    MAX_ROUNDS = "max_rounds"
    MAX_ACTIONS = "max_actions"
    NO_EVIDENCE_COLLECTED = "no_evidence_collected"


@dataclass(slots=True, frozen=True)
class SpecialistLoopToolDecision:
    """
    يمثل قرار الحلقة بشأن طلب أداة من الاختصاصي.
    """
    round_number: int
    tool_id: str
    rationale: str
    decision: str
    reasons: tuple[str, ...]
    evidence_id: str | None = None


@dataclass(slots=True, frozen=True)
class SpecialistLoopRoundTrace:
    """
    يمثل أثر جولة واحدة من reasoning ونتيجة أداة الاختصاصي.
    """
    round_number: int
    requested_tools: tuple[str, ...]
    collected_evidence_ids: tuple[str, ...]
    tool_decisions: tuple[
        SpecialistLoopToolDecision,
        ...
    ]
    confidence: float


@dataclass(slots=True, frozen=True)
class SpecialistInvestigationLoopResult:
    """
    يمثل النتيجة النهائية لحلقة التحقيق الخاصة بالاختصاصي.
    """
    final_result: SpecialistResult
    evidence: tuple[EvidenceReference, ...]
    rounds_completed: int
    actions_executed: int
    investigation_actions_used: int
    stop_reason: SpecialistLoopStopReason
    provider: str
    model: str
    traces: tuple[
        SpecialistLoopRoundTrace,
        ...
    ]


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
        """
        يهيئ SpecialistInvestigationLoop ويربط الاعتماديات اللازمة لدورة التحقيق.
        """
        self._context_builder = context_builder
        self._reasoning_agent = reasoning_agent
        self._diagnostic_tool_registry = (
            diagnostic_tool_registry
        )
        self._diagnostic_policy_engine = (
            diagnostic_policy_engine
        )
        self._evidence_collection_service = (
            evidence_collection_service
        )

    async def run(
        self,
        *,
        task: SpecialistTask,
        specialist: SpecialistRuntimeDefinition,
        investigation_budget: InvestigationBudget,
        detected_domains: tuple[str, ...] = (),
        initial_evidence: tuple[
            EvidenceReference,
            ...
        ] = (),
        initial_analysis_summary: str | None = None,
        initial_analysis_issues: tuple[dict, ...] = (),
        incident_contexts=(),
        allowed_specialist_slugs: tuple[str, ...] = (),
        investigation_actions_used: int = 0,
    ) -> SpecialistInvestigationLoopResult:
        """
        يدير جولات reasoning واستدعاء الأدوات حتى نتيجة أو حد توقف.
        """
        if (
            task.specialist_id.strip().casefold()
            != specialist.slug
        ):
            raise ValueError(
                "Task specialist does not match "
                "Specialist definition."
            )

        if investigation_actions_used < 0:
            raise ValueError(
                "investigation_actions_used must be >= 0."
            )

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

        catalog = self._render_tool_catalog(
            specialist
        )

        final_execution: (
            SpecialistReasoningExecution | None
        ) = None

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

            decisions: list[
                SpecialistLoopToolDecision
            ] = []

            round_evidence_ids: list[str] = []

            for requested in requests:
                # يحد النظام عدد الفحوص حتى لا يستمر التحقيق بلا نهاية أو
                # يستهلك متطلبات الحالة كلها في متابع واحد.
                if (
                    specialist_actions_used
                    >= specialist.max_actions
                    or global_actions_used
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
                                global_actions_used
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
                global_actions_used += 1

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

        return SpecialistInvestigationLoopResult(
            final_result=(
                final_execution.result
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
    def _request_signature(
        call: DiagnosticToolCall,
    ) -> str:
        """
        ينشئ توقيعًا ثابتًا لطلب أداة لمنع التكرار.
        """
        normalized_arguments = (
            json.dumps(
                call.arguments,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )

        return (
            call.tool_id.strip().casefold()
            + ":"
            + normalized_arguments
        )
