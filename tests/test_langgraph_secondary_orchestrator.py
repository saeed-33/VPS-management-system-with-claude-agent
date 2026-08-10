import asyncio
from dataclasses import dataclass
from types import MappingProxyType

from app.agent.investigation.contracts import (
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
from app.agent.investigation.langgraph_secondary_orchestrator import (
    DynamicSecondaryLangGraphCoordinator,
)
from app.agent.investigation.server_coordinator import (
    ServerCoordinatorResult,
    ServerCoordinatorSpecialistRun,
)
from app.agent.investigation.specialist_registry import (
    SpecialistRegistrySnapshot,
    SpecialistRuntimeDefinition,
)


def definition(
    slug,
    identifier,
):
    return SpecialistRuntimeDefinition(
        id=identifier,
        slug=slug,
        name=slug,
        description=None,
        instructions=None,
        domains=(slug,),
        trigger_hints=(),
        knowledge_topics=(),
        allowed_tool_ids=(),
        priority=10,
        max_rounds=3,
        max_actions=5,
        metadata=MappingProxyType({}),
    )


class Registry:
    def __init__(
        self,
        definitions,
    ):
        self._snapshot = (
            SpecialistRegistrySnapshot
            .build(definitions)
        )

    def snapshot(self):
        return self._snapshot


@dataclass
class FakeLoopResult:
    investigation_actions_used: int
    actions_executed: int = 0
    rounds_completed: int = 1
    evidence: tuple = ()
    stop_reason: object = None


class ParallelCoordinator:
    def __init__(
        self,
        recommendations,
        action_usage=None,
    ):
        self.recommendations = recommendations
        self.action_usage = action_usage or {}
        self.calls = []

    async def run(
        self,
        **kwargs,
    ):
        self.calls.append(kwargs)

        decision = kwargs[
            "routing_decision"
        ]
        investigation_id = kwargs[
            "investigation_id"
        ]
        budget = kwargs["budget"]

        state = ServerInvestigationState(
            investigation_id=(
                investigation_id
            ),
            server_id=kwargs[
                "server_id"
            ],
            report_id=kwargs[
                "report_id"
            ],
            analysis_id=kwargs[
                "analysis_id"
            ],
            status=(
                InvestigationStatus
                .COMPLETED
            ),
            budget=budget,
        )

        runs = []
        total_actions = 0

        for match in (
            decision
            .selected_specialists
        ):
            slug = (
                match.specialist_slug
            )
            used = min(
                self.action_usage.get(
                    slug,
                    0,
                ),
                budget.max_actions,
            )
            total_actions += used

            task = SpecialistTask(
                task_id=(
                    f"{investigation_id}:"
                    f"{slug}:1"
                ),
                investigation_id=(
                    investigation_id
                ),
                server_id=kwargs[
                    "server_id"
                ],
                report_id=kwargs[
                    "report_id"
                ],
                specialist_id=slug,
                objective="test",
                status=(
                    SpecialistTaskStatus
                    .COMPLETED
                ),
            )
            result = SpecialistResult(
                task_id=task.task_id,
                specialist_id=slug,
                status=(
                    SpecialistTaskStatus
                    .COMPLETED
                ),
                summary=(
                    f"{slug} complete"
                ),
                confidence=0.8,
                recommended_next_specialists=tuple(
                    self.recommendations
                    .get(slug, ())
                ),
            )
            state.add_task(task)
            state.add_result(result)

            runs.append(
                ServerCoordinatorSpecialistRun(
                    specialist_slug=slug,
                    task=task,
                    result=result,
                    loop_result=(
                        FakeLoopResult(
                            investigation_actions_used=(
                                used
                            ),
                            actions_executed=used,
                        )
                    ),
                )
            )

        return ServerCoordinatorResult(
            state=state,
            runs=tuple(runs),
            investigation_actions_used=(
                total_actions
            ),
        )


def decision(
    *slugs,
):
    matches = tuple(
        SpecialistRoutingMatch(
            specialist_id=index,
            specialist_slug=slug,
            specialist_name=slug,
            score=1,
            matched_domains=(slug,),
            matched_trigger_hints=(),
            matched_issue_indexes=(),
            priority=10,
        )
        for index, slug
        in enumerate(
            slugs,
            start=1,
        )
    )

    return InvestigationRoutingDecision(
        should_investigate=True,
        reasons=(),
        detected_domains=tuple(
            slugs
        ),
        candidate_specialists=matches,
        selected_specialists=matches,
        unmatched_issue_indexes=(),
        registry_size=4,
        candidate_limit=4,
        selection_limit=4,
    )


def registry():
    return Registry(
        (
            definition(
                "nginx",
                1,
            ),
            definition(
                "systemd-service",
                2,
            ),
            definition(
                "linux-network",
                3,
            ),
            definition(
                "linux-memory",
                4,
            ),
        )
    )


def test_recommendation_creates_secondary_wave():
    parallel = ParallelCoordinator(
        {
            "nginx": (
                "systemd-service",
            ),
        }
    )

    coordinator = (
        DynamicSecondaryLangGraphCoordinator(
            specialist_registry=(
                registry()
            ),
            parallel_coordinator=(
                parallel
            ),
        )
    )

    output = asyncio.run(
        coordinator.run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=(
                decision("nginx")
            ),
            budget=(
                InvestigationBudget(
                    max_specialists=3,
                    max_rounds=3,
                    max_actions=8,
                )
            ),
        )
    )

    assert len(parallel.calls) == 2
    assert [
        run.specialist_slug
        for run in output.runs
    ] == [
        "nginx",
        "systemd-service",
    ]
    assert (
        output.state.metadata[
            "waves_completed"
        ]
        == 2
    )


def test_already_run_recommendation_is_not_repeated():
    parallel = ParallelCoordinator(
        {
            "nginx": ("nginx",),
        }
    )

    output = asyncio.run(
        DynamicSecondaryLangGraphCoordinator(
            specialist_registry=registry(),
            parallel_coordinator=parallel,
        ).run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=decision(
                "nginx"
            ),
        )
    )

    assert len(parallel.calls) == 1
    assert [
        run.specialist_slug
        for run in output.runs
    ] == ["nginx"]
    assert (
        output.state.metadata[
            "secondary_decisions"
        ][0]["dropped_already_run"]
        == ["nginx"]
    )


def test_unknown_recommendation_is_dropped():
    parallel = ParallelCoordinator(
        {
            "nginx": (
                "not-enabled",
            ),
        }
    )

    output = asyncio.run(
        DynamicSecondaryLangGraphCoordinator(
            specialist_registry=registry(),
            parallel_coordinator=parallel,
        ).run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=decision(
                "nginx"
            ),
        )
    )

    assert len(parallel.calls) == 1
    assert (
        output.state.metadata[
            "secondary_decisions"
        ][0]["dropped_unavailable"]
        == ["not-enabled"]
    )


def test_max_specialists_blocks_extra_followups():
    parallel = ParallelCoordinator(
        {
            "nginx": (
                "systemd-service",
                "linux-network",
            ),
        }
    )

    output = asyncio.run(
        DynamicSecondaryLangGraphCoordinator(
            specialist_registry=registry(),
            parallel_coordinator=parallel,
        ).run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=decision(
                "nginx"
            ),
            budget=(
                InvestigationBudget(
                    max_specialists=2,
                    max_rounds=3,
                    max_actions=8,
                )
            ),
        )
    )

    assert [
        run.specialist_slug
        for run in output.runs
    ] == [
        "nginx",
        "systemd-service",
    ]
    assert (
        output.state.metadata[
            "secondary_decisions"
        ][0]["dropped_budget"]
        == ["linux-network"]
    )


def test_remaining_action_budget_is_passed_to_next_wave():
    parallel = ParallelCoordinator(
        {
            "nginx": (
                "systemd-service",
            ),
        },
        action_usage={
            "nginx": 3,
            "systemd-service": 2,
        },
    )

    output = asyncio.run(
        DynamicSecondaryLangGraphCoordinator(
            specialist_registry=registry(),
            parallel_coordinator=parallel,
        ).run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=decision(
                "nginx"
            ),
            budget=(
                InvestigationBudget(
                    max_specialists=3,
                    max_rounds=3,
                    max_actions=8,
                )
            ),
        )
    )

    assert (
        parallel.calls[0][
            "budget"
        ].max_actions
        == 8
    )
    assert (
        parallel.calls[1][
            "budget"
        ].max_actions
        == 5
    )
    assert (
        output
        .investigation_actions_used
        == 5
    )


def test_secondary_can_recommend_tertiary_within_limits():
    parallel = ParallelCoordinator(
        {
            "nginx": (
                "systemd-service",
            ),
            "systemd-service": (
                "linux-network",
            ),
        }
    )

    output = asyncio.run(
        DynamicSecondaryLangGraphCoordinator(
            specialist_registry=registry(),
            parallel_coordinator=parallel,
        ).run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=decision(
                "nginx"
            ),
            budget=(
                InvestigationBudget(
                    max_specialists=3,
                    max_rounds=3,
                    max_actions=8,
                )
            ),
        )
    )

    assert [
        run.specialist_slug
        for run in output.runs
    ] == [
        "nginx",
        "systemd-service",
        "linux-network",
    ]
    assert (
        output.state.metadata[
            "waves_completed"
        ]
        == 3
    )
