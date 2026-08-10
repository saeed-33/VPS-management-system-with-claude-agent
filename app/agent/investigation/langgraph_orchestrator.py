from __future__ import annotations

import operator
from dataclasses import dataclass, replace
from typing import Annotated
from uuid import uuid4

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from app.agent.investigation.contracts import (
    EvidenceReference,
    InvestigationBudget,
    InvestigationStatus,
    ServerInvestigationState,
    SpecialistResult,
    SpecialistTask,
    SpecialistTaskStatus,
)
from app.agent.investigation.investigation_router import (
    InvestigationRoutingDecision,
    SpecialistRoutingMatch,
)
from app.agent.investigation.server_coordinator import (
    ServerCoordinator,
    ServerCoordinatorResult,
    ServerCoordinatorSpecialistRun,
)
from app.agent.investigation.specialist_investigation_loop import (
    SpecialistInvestigationLoop,
)
from app.agent.investigation.specialist_registry import (
    SpecialistRegistry,
    SpecialistRuntimeDefinition,
)


@dataclass(slots=True, frozen=True)
class SpecialistWorkerAssignment:
    selection_index: int
    match: SpecialistRoutingMatch
    specialist: SpecialistRuntimeDefinition | None
    action_quota: int


class InvestigationGraphState(TypedDict, total=False):
    server_id: int
    report_id: int
    analysis_id: int | None
    routing_decision: InvestigationRoutingDecision
    budget: InvestigationBudget
    initial_analysis_summary: str | None
    initial_analysis_issues: tuple[dict, ...]
    incident_contexts: tuple
    initial_evidence: tuple[EvidenceReference, ...]
    investigation_id: str
    assignments: tuple[SpecialistWorkerAssignment, ...]
    baseline_evidence: tuple[EvidenceReference, ...]
    allowed_specialist_slugs: tuple[str, ...]
    worker_runs: Annotated[
        list[ServerCoordinatorSpecialistRun],
        operator.add,
    ]
    result: ServerCoordinatorResult


class SpecialistWorkerState(TypedDict):
    server_id: int
    report_id: int
    analysis_id: int | None
    investigation_id: str
    routing_decision: InvestigationRoutingDecision
    original_budget: InvestigationBudget
    assignment: SpecialistWorkerAssignment
    baseline_evidence: tuple[EvidenceReference, ...]
    allowed_specialist_slugs: tuple[str, ...]
    initial_analysis_summary: str | None
    initial_analysis_issues: tuple[dict, ...]
    incident_contexts: tuple


class LangGraphServerCoordinator:
    """
    Phase 4.16 LangGraph orchestration boundary.

    The graph owns parallel fan-out/fan-in only. Specialist reasoning,
    Tool Policy, Evidence Collection, SSH, and RAG remain in existing
    services.

    Global action safety uses deterministic pre-allocation. Each parallel
    worker receives an isolated quota and the sum of all quotas is never
    greater than InvestigationBudget.max_actions.
    """

    def __init__(
        self,
        *,
        specialist_registry: SpecialistRegistry,
        specialist_loop: SpecialistInvestigationLoop,
        max_concurrency: int = 4,
    ) -> None:
        if max_concurrency < 1:
            raise ValueError(
                "max_concurrency must be >= 1."
            )

        self._specialist_registry = (
            specialist_registry
        )
        self._specialist_loop = (
            specialist_loop
        )
        self._max_concurrency = (
            max_concurrency
        )
        self._graph = self._build_graph()

    async def run(
        self,
        *,
        server_id: int,
        report_id: int,
        analysis_id: int | None,
        routing_decision: InvestigationRoutingDecision,
        budget: InvestigationBudget | None = None,
        initial_analysis_summary: str | None = None,
        initial_analysis_issues: tuple[dict, ...] = (),
        incident_contexts=(),
        initial_evidence=(),
        investigation_id: str | None = None,
    ) -> ServerCoordinatorResult:
        effective_budget = (
            budget
            or InvestigationBudget()
        )

        output = await self._graph.ainvoke(
            {
                "server_id": server_id,
                "report_id": report_id,
                "analysis_id": analysis_id,
                "routing_decision": routing_decision,
                "budget": effective_budget,
                "initial_analysis_summary": (
                    initial_analysis_summary
                ),
                "initial_analysis_issues": (
                    initial_analysis_issues
                ),
                "incident_contexts": tuple(
                    incident_contexts
                ),
                "initial_evidence": tuple(
                    initial_evidence
                ),
                "investigation_id": (
                    investigation_id
                    or str(uuid4())
                ),
                "worker_runs": [],
            },
            config={
                "max_concurrency": (
                    self._max_concurrency
                ),
            },
        )

        return output["result"]

    def _build_graph(self):
        builder = StateGraph(
            InvestigationGraphState
        )

        builder.add_node(
            "prepare",
            self._prepare,
        )
        builder.add_node(
            "run_specialist",
            self._run_specialist,
        )
        builder.add_node(
            "aggregate",
            self._aggregate,
        )

        builder.add_edge(
            START,
            "prepare",
        )

        builder.add_conditional_edges(
            "prepare",
            self._fan_out,
            [
                "run_specialist",
                "aggregate",
            ],
        )

        builder.add_edge(
            "run_specialist",
            "aggregate",
        )

        builder.add_edge(
            "aggregate",
            END,
        )

        return builder.compile()

    async def _prepare(
        self,
        state: InvestigationGraphState,
    ):
        decision = state[
            "routing_decision"
        ]
        budget = state["budget"]

        snapshot = (
            self._specialist_registry
            .snapshot()
        )

        baseline = list(
            ServerCoordinator
            ._analysis_evidence(
                report_id=state["report_id"],
                analysis_id=state["analysis_id"],
                summary=state.get(
                    "initial_analysis_summary"
                ),
                issues=state.get(
                    "initial_analysis_issues",
                    (),
                ),
            )
        )

        seen = {
            item.evidence_id
            for item in baseline
        }

        for item in state.get(
            "initial_evidence",
            (),
        ):
            if item.evidence_id not in seen:
                baseline.append(item)
                seen.add(
                    item.evidence_id
                )

        selected = (
            decision.selected_specialists[
                : budget.max_specialists
            ]
            if decision.should_investigate
            else ()
        )

        quotas = self._allocate_actions(
            total_actions=(
                budget.max_actions
            ),
            worker_count=len(selected),
        )

        assignments = tuple(
            SpecialistWorkerAssignment(
                selection_index=index,
                match=match,
                specialist=(
                    snapshot.get_by_slug(
                        match.specialist_slug
                    )
                ),
                action_quota=quotas[index],
            )
            for index, match
            in enumerate(selected)
        )

        return {
            "assignments": assignments,
            "baseline_evidence": tuple(
                baseline
            ),
            "allowed_specialist_slugs": (
                tuple(
                    item.slug
                    for item
                    in snapshot.definitions
                )
            ),
        }

    def _fan_out(
        self,
        state: InvestigationGraphState,
    ):
        assignments = state.get(
            "assignments",
            (),
        )

        if not assignments:
            return "aggregate"

        return [
            Send(
                "run_specialist",
                {
                    "server_id": (
                        state["server_id"]
                    ),
                    "report_id": (
                        state["report_id"]
                    ),
                    "analysis_id": (
                        state["analysis_id"]
                    ),
                    "investigation_id": (
                        state[
                            "investigation_id"
                        ]
                    ),
                    "routing_decision": (
                        state[
                            "routing_decision"
                        ]
                    ),
                    "original_budget": (
                        state["budget"]
                    ),
                    "assignment": (
                        assignment
                    ),
                    "baseline_evidence": (
                        state[
                            "baseline_evidence"
                        ]
                    ),
                    "allowed_specialist_slugs": (
                        state[
                            "allowed_specialist_slugs"
                        ]
                    ),
                    "initial_analysis_summary": (
                        state.get(
                            "initial_analysis_summary"
                        )
                    ),
                    "initial_analysis_issues": (
                        state.get(
                            "initial_analysis_issues",
                            (),
                        )
                    ),
                    "incident_contexts": (
                        state.get(
                            "incident_contexts",
                            (),
                        )
                    ),
                },
            )
            for assignment
            in assignments
        ]

    async def _run_specialist(
        self,
        state: SpecialistWorkerState,
    ):
        assignment = state[
            "assignment"
        ]
        match = assignment.match
        specialist = (
            assignment.specialist
        )

        task = SpecialistTask(
            task_id=(
                f"{state['investigation_id']}:"
                f"{match.specialist_slug}:1"
            ),
            investigation_id=(
                state["investigation_id"]
            ),
            server_id=(
                state["server_id"]
            ),
            report_id=(
                state["report_id"]
            ),
            specialist_id=(
                match.specialist_slug
            ),
            objective=(
                ServerCoordinator
                ._build_objective(
                    specialist_name=(
                        match.specialist_name
                    ),
                    matched_domains=(
                        match.matched_domains
                    ),
                    matched_issue_indexes=(
                        match
                        .matched_issue_indexes
                    ),
                )
            ),
            trigger_issue_ids=tuple(
                f"analysis-issue:{index}"
                for index
                in match.matched_issue_indexes
            ),
            evidence_ids=tuple(
                item.evidence_id
                for item
                in state[
                    "baseline_evidence"
                ]
            ),
            knowledge_topics=(
                specialist.knowledge_topics
                if specialist is not None
                else ()
            ),
            status=(
                SpecialistTaskStatus.RUNNING
            ),
            metadata={
                "langgraph_selection_index": (
                    assignment
                    .selection_index
                ),
                "parallel_action_quota": (
                    assignment
                    .action_quota
                ),
            },
        )

        if specialist is None:
            failed = SpecialistResult(
                task_id=task.task_id,
                specialist_id=(
                    task.specialist_id
                ),
                status=(
                    SpecialistTaskStatus.FAILED
                ),
                summary=(
                    "Selected Specialist is "
                    "unavailable in the runtime "
                    "registry snapshot."
                ),
                confidence=0.0,
                missing_evidence=(
                    "Enabled Specialist runtime "
                    "definition.",
                ),
                metadata={
                    "coordinator_failure": (
                        "specialist_unavailable"
                    ),
                    "langgraph_selection_index": (
                        assignment
                        .selection_index
                    ),
                },
            )

            run = (
                ServerCoordinatorSpecialistRun(
                    specialist_slug=(
                        match.specialist_slug
                    ),
                    task=replace(
                        task,
                        status=(
                            SpecialistTaskStatus
                            .FAILED
                        ),
                    ),
                    result=failed,
                    loop_result=None,
                )
            )

            return {
                "worker_runs": [run],
            }

        try:
            worker_budget = (
                InvestigationBudget(
                    max_specialists=1,
                    max_rounds=(
                        state[
                            "original_budget"
                        ].max_rounds
                    ),
                    max_actions=(
                        assignment
                        .action_quota
                    ),
                )
            )

            loop_result = await (
                self._specialist_loop.run(
                    task=task,
                    specialist=specialist,
                    investigation_budget=(
                        worker_budget
                    ),
                    detected_domains=tuple(
                        state[
                            "routing_decision"
                        ].detected_domains
                    ),
                    initial_evidence=(
                        state[
                            "baseline_evidence"
                        ]
                    ),
                    initial_analysis_summary=(
                        state.get(
                            "initial_analysis_summary"
                        )
                    ),
                    initial_analysis_issues=(
                        state.get(
                            "initial_analysis_issues",
                            (),
                        )
                    ),
                    incident_contexts=(
                        state.get(
                            "incident_contexts",
                            (),
                        )
                    ),
                    allowed_specialist_slugs=(
                        state[
                            "allowed_specialist_slugs"
                        ]
                    ),
                    # Each branch owns an isolated
                    # quota. Local action counting
                    # starts at zero.
                    investigation_actions_used=0,
                )
            )

            result = (
                loop_result.final_result
            )

            run = (
                ServerCoordinatorSpecialistRun(
                    specialist_slug=(
                        specialist.slug
                    ),
                    task=replace(
                        task,
                        status=result.status,
                    ),
                    result=result,
                    loop_result=(
                        loop_result
                    ),
                )
            )

        except Exception as exc:
            failed = SpecialistResult(
                task_id=task.task_id,
                specialist_id=(
                    task.specialist_id
                ),
                status=(
                    SpecialistTaskStatus.FAILED
                ),
                summary=(
                    "Parallel Specialist "
                    "investigation failed before "
                    "a valid result was produced."
                ),
                confidence=0.0,
                metadata={
                    "coordinator_failure": (
                        type(exc).__name__
                    ),
                    "error": str(exc),
                    "langgraph_selection_index": (
                        assignment
                        .selection_index
                    ),
                },
            )

            run = (
                ServerCoordinatorSpecialistRun(
                    specialist_slug=(
                        specialist.slug
                    ),
                    task=replace(
                        task,
                        status=(
                            SpecialistTaskStatus
                            .FAILED
                        ),
                    ),
                    result=failed,
                    loop_result=None,
                )
            )

        return {
            "worker_runs": [run],
        }

    async def _aggregate(
        self,
        state: InvestigationGraphState,
    ):
        decision = state[
            "routing_decision"
        ]
        budget = state["budget"]

        server_state = (
            ServerInvestigationState(
                investigation_id=(
                    state[
                        "investigation_id"
                    ]
                ),
                server_id=state["server_id"],
                report_id=state["report_id"],
                analysis_id=state[
                    "analysis_id"
                ],
                status=(
                    InvestigationStatus.CREATED
                ),
                budget=budget,
                detected_domains=list(
                    decision.detected_domains
                ),
            )
        )

        for evidence in state.get(
            "baseline_evidence",
            (),
        ):
            server_state.add_evidence(
                evidence
            )

        assignments = {
            item.match.specialist_slug:
            item
            for item
            in state.get(
                "assignments",
                (),
            )
        }

        runs = sorted(
            state.get(
                "worker_runs",
                [],
            ),
            key=lambda item: (
                assignments[
                    item.specialist_slug
                ].selection_index
                if item.specialist_slug
                in assignments
                else 10**9
            ),
        )

        total_actions = 0

        for run in runs:
            server_state.add_task(
                run.task
            )

            if (
                run.loop_result
                is not None
            ):
                total_actions += (
                    run.loop_result
                    .investigation_actions_used
                )

                known = {
                    item.evidence_id
                    for item
                    in server_state.evidence
                }

                for evidence in (
                    run.loop_result
                    .evidence
                ):
                    if (
                        evidence.evidence_id
                        not in known
                    ):
                        server_state.add_evidence(
                            evidence
                        )
                        known.add(
                            evidence
                            .evidence_id
                        )

            server_state.add_result(
                run.result
            )

        if (
            not decision.should_investigate
        ):
            server_state.status = (
                InvestigationStatus.COMPLETED
            )
            stop_reason = (
                "investigation_not_required"
            )

        elif not runs:
            server_state.status = (
                InvestigationStatus.COMPLETED
            )
            stop_reason = (
                "no_selected_specialists"
            )

        elif all(
            item.result.status
            == SpecialistTaskStatus.FAILED
            for item in runs
        ):
            server_state.status = (
                InvestigationStatus.FAILED
            )
            stop_reason = (
                "all_specialists_failed"
            )

        else:
            server_state.status = (
                InvestigationStatus.COMPLETED
            )
            stop_reason = (
                "parallel_specialists_complete"
            )

        quota_total = sum(
            item.action_quota
            for item
            in state.get(
                "assignments",
                (),
            )
        )

        server_state.metadata.update(
            {
                "orchestrator": (
                    "langgraph"
                ),
                "execution_mode": (
                    "parallel"
                ),
                "coordinator_stop_reason": (
                    stop_reason
                ),
                "investigation_actions_used": (
                    total_actions
                ),
                "parallel_action_quota_total": (
                    quota_total
                ),
                "max_concurrency": (
                    self._max_concurrency
                ),
                "selected_specialists": [
                    item.match.specialist_slug
                    for item
                    in state.get(
                        "assignments",
                        (),
                    )
                ],
                "completed_specialists": [
                    item.specialist_slug
                    for item in runs
                    if item.result.status
                    == SpecialistTaskStatus
                    .COMPLETED
                ],
                "failed_specialists": [
                    item.specialist_slug
                    for item in runs
                    if item.result.status
                    == SpecialistTaskStatus
                    .FAILED
                ],
            }
        )

        if total_actions > budget.max_actions:
            raise RuntimeError(
                "Parallel Specialist action "
                "usage exceeded the global "
                "Investigation budget."
            )

        result = ServerCoordinatorResult(
            state=server_state,
            runs=tuple(runs),
            investigation_actions_used=(
                total_actions
            ),
        )

        return {
            "result": result,
        }

    @staticmethod
    def _allocate_actions(
        *,
        total_actions: int,
        worker_count: int,
    ) -> tuple[int, ...]:
        if worker_count < 0:
            raise ValueError(
                "worker_count must be >= 0."
            )

        if worker_count == 0:
            return ()

        base, remainder = divmod(
            total_actions,
            worker_count,
        )

        return tuple(
            base
            + (
                1
                if index < remainder
                else 0
            )
            for index
            in range(worker_count)
        )
