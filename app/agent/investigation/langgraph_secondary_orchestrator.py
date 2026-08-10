from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agent.investigation.contracts import (
    EvidenceReference,
    InvestigationBudget,
    InvestigationStatus,
    ServerInvestigationState,
    SpecialistTaskStatus,
)
from app.agent.investigation.investigation_router import (
    InvestigationRoutingDecision,
    SpecialistRoutingMatch,
)
from app.agent.investigation.langgraph_orchestrator import (
    LangGraphServerCoordinator,
)
from app.agent.investigation.server_coordinator import (
    ServerCoordinatorResult,
    ServerCoordinatorSpecialistRun,
)
from app.agent.investigation.specialist_registry import (
    SpecialistRegistry,
)


@dataclass(slots=True, frozen=True)
class SecondaryRecommendationDecision:
    requested: tuple[str, ...]
    accepted: tuple[str, ...]
    dropped_already_run: tuple[str, ...]
    dropped_unavailable: tuple[str, ...]
    dropped_budget: tuple[str, ...]


class SecondaryInvestigationGraphState(
    TypedDict,
    total=False,
):
    server_id: int
    report_id: int
    analysis_id: int | None
    investigation_id: str
    initial_decision: InvestigationRoutingDecision
    current_decision: InvestigationRoutingDecision
    original_budget: InvestigationBudget
    initial_analysis_summary: str | None
    initial_analysis_issues: tuple[dict, ...]
    incident_contexts: tuple
    initial_evidence: tuple[EvidenceReference, ...]
    accumulated_evidence: tuple[EvidenceReference, ...]
    accumulated_runs: tuple[ServerCoordinatorSpecialistRun, ...]
    executed_slugs: tuple[str, ...]
    actions_used: int
    wave_index: int
    current_wave_result: ServerCoordinatorResult
    recommendation_history: tuple[
        SecondaryRecommendationDecision,
        ...
    ]
    result: ServerCoordinatorResult


class DynamicSecondaryLangGraphCoordinator:
    """
    Phase 4.17 dynamic follow-up Specialist routing.

    This graph is deliberately layered over the accepted Phase 4.16
    LangGraphServerCoordinator. Each wave can fan out in parallel using
    the 4.16 graph; this outer graph decides whether another bounded wave
    is justified from `recommended_next_specialists`.

    Safety invariants:
    - only enabled Registry Specialists can be accepted;
    - a Specialist is never run twice in one Investigation;
    - total Specialists never exceeds InvestigationBudget.max_specialists;
    - each later wave receives only remaining action budget;
    - total actions never exceeds InvestigationBudget.max_actions.
    """

    def __init__(
        self,
        *,
        specialist_registry: SpecialistRegistry,
        parallel_coordinator: LangGraphServerCoordinator,
    ) -> None:
        self._specialist_registry = specialist_registry
        self._parallel_coordinator = parallel_coordinator
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
        effective_budget = budget or InvestigationBudget()

        output = await self._graph.ainvoke(
            {
                "server_id": server_id,
                "report_id": report_id,
                "analysis_id": analysis_id,
                "investigation_id": (
                    investigation_id or str(uuid4())
                ),
                "initial_decision": routing_decision,
                "current_decision": routing_decision,
                "original_budget": effective_budget,
                "initial_analysis_summary": initial_analysis_summary,
                "initial_analysis_issues": initial_analysis_issues,
                "incident_contexts": tuple(incident_contexts),
                "initial_evidence": tuple(initial_evidence),
                "accumulated_evidence": tuple(initial_evidence),
                "accumulated_runs": (),
                "executed_slugs": (),
                "actions_used": 0,
                "wave_index": 0,
                "recommendation_history": (),
            }
        )

        return output["result"]

    def _build_graph(self):
        builder = StateGraph(
            SecondaryInvestigationGraphState
        )

        builder.add_node(
            "run_wave",
            self._run_wave,
        )
        builder.add_node(
            "plan_secondary",
            self._plan_secondary,
        )
        builder.add_node(
            "finalize",
            self._finalize,
        )

        builder.add_edge(
            START,
            "run_wave",
        )
        builder.add_edge(
            "run_wave",
            "plan_secondary",
        )
        builder.add_conditional_edges(
            "plan_secondary",
            self._next_step,
            {
                "run_wave": "run_wave",
                "finalize": "finalize",
            },
        )
        builder.add_edge(
            "finalize",
            END,
        )

        return builder.compile()

    async def _run_wave(
        self,
        state: SecondaryInvestigationGraphState,
    ):
        original_budget = state["original_budget"]
        remaining_actions = max(
            0,
            original_budget.max_actions
            - state.get("actions_used", 0),
        )
        remaining_specialists = max(
            0,
            original_budget.max_specialists
            - len(state.get("executed_slugs", ())),
        )

        decision = state["current_decision"]

        if state.get("wave_index", 0) == 0:
            wave_specialist_limit = min(
                remaining_specialists,
                max(
                    1,
                    len(decision.selected_specialists),
                ),
            )
        else:
            wave_specialist_limit = remaining_specialists

        wave_budget = InvestigationBudget(
            max_specialists=max(
                1,
                wave_specialist_limit,
            ),
            max_rounds=original_budget.max_rounds,
            max_actions=remaining_actions,
        )

        result = await self._parallel_coordinator.run(
            server_id=state["server_id"],
            report_id=state["report_id"],
            analysis_id=state["analysis_id"],
            routing_decision=decision,
            budget=wave_budget,
            initial_analysis_summary=state.get(
                "initial_analysis_summary"
            ),
            initial_analysis_issues=state.get(
                "initial_analysis_issues",
                (),
            ),
            incident_contexts=state.get(
                "incident_contexts",
                (),
            ),
            initial_evidence=state.get(
                "accumulated_evidence",
                (),
            ),
            investigation_id=state["investigation_id"],
        )

        known_evidence = {
            item.evidence_id
            for item
            in state.get(
                "accumulated_evidence",
                (),
            )
        }
        merged_evidence = list(
            state.get(
                "accumulated_evidence",
                (),
            )
        )

        for item in result.state.evidence:
            if item.evidence_id not in known_evidence:
                merged_evidence.append(item)
                known_evidence.add(item.evidence_id)

        previous_runs = state.get(
            "accumulated_runs",
            (),
        )
        new_runs = tuple(result.runs)

        executed = list(
            state.get(
                "executed_slugs",
                (),
            )
        )
        for run in new_runs:
            if run.specialist_slug not in executed:
                executed.append(run.specialist_slug)

        return {
            "current_wave_result": result,
            "accumulated_evidence": tuple(
                merged_evidence
            ),
            "accumulated_runs": (
                previous_runs + new_runs
            ),
            "executed_slugs": tuple(executed),
            "actions_used": (
                state.get("actions_used", 0)
                + result.investigation_actions_used
            ),
            "wave_index": (
                state.get("wave_index", 0)
                + 1
            ),
        }

    async def _plan_secondary(
        self,
        state: SecondaryInvestigationGraphState,
    ):
        original_budget = state["original_budget"]
        executed = tuple(
            state.get(
                "executed_slugs",
                (),
            )
        )
        executed_set = set(executed)

        remaining_slots = max(
            0,
            original_budget.max_specialists
            - len(executed),
        )
        remaining_actions = max(
            0,
            original_budget.max_actions
            - state.get("actions_used", 0),
        )

        current_result = state[
            "current_wave_result"
        ]

        requested_ordered: list[str] = []
        requested_seen: set[str] = set()

        for run in current_result.runs:
            for slug in (
                run.result
                .recommended_next_specialists
            ):
                normalized = slug.strip()
                if (
                    normalized
                    and normalized
                    not in requested_seen
                ):
                    requested_ordered.append(
                        normalized
                    )
                    requested_seen.add(
                        normalized
                    )

        snapshot = (
            self._specialist_registry
            .snapshot()
        )
        available = {
            item.slug: item
            for item
            in snapshot.definitions
        }

        dropped_already: list[str] = []
        dropped_unavailable: list[str] = []
        eligible: list[str] = []

        for slug in requested_ordered:
            if slug in executed_set:
                dropped_already.append(slug)
            elif slug not in available:
                dropped_unavailable.append(slug)
            else:
                eligible.append(slug)

        accepted = tuple(
            eligible[:remaining_slots]
            if remaining_actions > 0
            else ()
        )

        dropped_budget = tuple(
            eligible[len(accepted):]
        )

        decision_record = (
            SecondaryRecommendationDecision(
                requested=tuple(
                    requested_ordered
                ),
                accepted=accepted,
                dropped_already_run=tuple(
                    dropped_already
                ),
                dropped_unavailable=tuple(
                    dropped_unavailable
                ),
                dropped_budget=dropped_budget,
            )
        )

        history = (
            state.get(
                "recommendation_history",
                (),
            )
            + (decision_record,)
        )

        if not accepted:
            return {
                "recommendation_history": history,
            }

        matches = tuple(
            SpecialistRoutingMatch(
                specialist_id=(
                    available[slug].id
                ),
                specialist_slug=slug,
                specialist_name=(
                    available[slug].name
                ),
                score=1,
                matched_domains=tuple(
                    available[slug].domains
                ),
                matched_trigger_hints=(),
                matched_issue_indexes=(),
                priority=(
                    available[slug].priority
                ),
            )
            for slug in accepted
        )

        next_decision = (
            InvestigationRoutingDecision(
                should_investigate=True,
                reasons=(),
                detected_domains=tuple(
                    sorted(
                        {
                            domain
                            for slug in accepted
                            for domain
                            in available[slug]
                            .domains
                        }
                    )
                ),
                candidate_specialists=matches,
                selected_specialists=matches,
                unmatched_issue_indexes=(),
                registry_size=len(
                    snapshot.definitions
                ),
                candidate_limit=max(
                    1,
                    len(matches),
                ),
                selection_limit=max(
                    1,
                    len(matches),
                ),
            )
        )

        return {
            "current_decision": next_decision,
            "recommendation_history": history,
        }

    def _next_step(
        self,
        state: SecondaryInvestigationGraphState,
    ) -> str:
        history = state.get(
            "recommendation_history",
            (),
        )

        if (
            history
            and history[-1].accepted
        ):
            return "run_wave"

        return "finalize"

    async def _finalize(
        self,
        state: SecondaryInvestigationGraphState,
    ):
        budget = state["original_budget"]
        runs = tuple(
            state.get(
                "accumulated_runs",
                (),
            )
        )
        evidence = tuple(
            state.get(
                "accumulated_evidence",
                (),
            )
        )

        server_state = ServerInvestigationState(
            investigation_id=state[
                "investigation_id"
            ],
            server_id=state["server_id"],
            report_id=state["report_id"],
            analysis_id=state["analysis_id"],
            status=InvestigationStatus.CREATED,
            budget=budget,
            detected_domains=list(
                state["initial_decision"]
                .detected_domains
            ),
        )

        for item in evidence:
            server_state.add_evidence(item)

        for run in runs:
            server_state.add_task(run.task)
            server_state.add_result(
                run.result
            )

        if (
            runs
            and all(
                run.result.status
                == SpecialistTaskStatus.FAILED
                for run in runs
            )
        ):
            server_state.status = (
                InvestigationStatus.FAILED
            )
        else:
            server_state.status = (
                InvestigationStatus.COMPLETED
            )

        history = state.get(
            "recommendation_history",
            (),
        )
        accepted_secondary = tuple(
            slug
            for item in history
            for slug in item.accepted
        )
        requested_secondary = tuple(
            slug
            for item in history
            for slug in item.requested
        )

        server_state.metadata.update(
            {
                "orchestrator": "langgraph",
                "execution_mode": (
                    "dynamic-secondary"
                ),
                "waves_completed": state.get(
                    "wave_index",
                    0,
                ),
                "investigation_actions_used": (
                    state.get(
                        "actions_used",
                        0,
                    )
                ),
                "executed_specialists": list(
                    state.get(
                        "executed_slugs",
                        (),
                    )
                ),
                "secondary_requested": list(
                    requested_secondary
                ),
                "secondary_accepted": list(
                    accepted_secondary
                ),
                "secondary_decisions": [
                    {
                        "requested": list(
                            item.requested
                        ),
                        "accepted": list(
                            item.accepted
                        ),
                        "dropped_already_run": list(
                            item.dropped_already_run
                        ),
                        "dropped_unavailable": list(
                            item.dropped_unavailable
                        ),
                        "dropped_budget": list(
                            item.dropped_budget
                        ),
                    }
                    for item in history
                ],
            }
        )

        actions_used = state.get(
            "actions_used",
            0,
        )

        if actions_used > budget.max_actions:
            raise RuntimeError(
                "Dynamic secondary routing "
                "exceeded the global action budget."
            )

        if (
            len(state.get(
                "executed_slugs",
                (),
            ))
            > budget.max_specialists
        ):
            raise RuntimeError(
                "Dynamic secondary routing "
                "exceeded max_specialists."
            )

        return {
            "result": (
                ServerCoordinatorResult(
                    state=server_state,
                    runs=runs,
                    investigation_actions_used=(
                        actions_used
                    ),
                )
            )
        }
