import asyncio
from dataclasses import dataclass
from types import MappingProxyType

from app.agent.investigation.contracts import (
    InvestigationBudget,
    SpecialistResult,
    SpecialistTaskStatus,
)
from app.agent.investigation.investigation_router import (
    InvestigationRoutingDecision,
    SpecialistRoutingMatch,
)
from app.agent.investigation.langgraph_orchestrator import (
    LangGraphServerCoordinator,
)
from app.agent.investigation.specialist_registry import (
    SpecialistRegistrySnapshot,
    SpecialistRuntimeDefinition,
)


def specialist(
    slug,
    *,
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
        max_actions=10,
        metadata=MappingProxyType({}),
    )


class Registry:
    def __init__(
        self,
        definitions,
    ):
        self._snapshot = (
            SpecialistRegistrySnapshot
            .build(
                definitions
            )
        )

    def snapshot(self):
        return self._snapshot


@dataclass
class LoopOutput:
    final_result: SpecialistResult
    evidence: tuple = ()
    investigation_actions_used: int = 0
    rounds_completed: int = 1
    actions_executed: int = 0
    stop_reason: object = None
    provider: str = "fake"
    model: str = "fake"


class ParallelLoop:
    def __init__(
        self,
        *,
        failures=(),
        delays=None,
        consume_full_quota=False,
    ):
        self.failures = set(failures)
        self.delays = (
            delays or {}
        )
        self.consume_full_quota = (
            consume_full_quota
        )
        self.calls = []
        self.active = 0
        self.max_active = 0

    async def run(
        self,
        **kwargs,
    ):
        slug = (
            kwargs["specialist"].slug
        )

        self.calls.append(
            kwargs
        )

        self.active += 1
        self.max_active = max(
            self.max_active,
            self.active,
        )

        try:
            await asyncio.sleep(
                self.delays.get(
                    slug,
                    0.03,
                )
            )

            if slug in self.failures:
                raise RuntimeError(
                    f"{slug} boom"
                )

            budget = kwargs[
                "investigation_budget"
            ]

            used = (
                budget.max_actions
                if self.consume_full_quota
                else min(
                    1,
                    budget.max_actions,
                )
            )

            return LoopOutput(
                final_result=(
                    SpecialistResult(
                        task_id=(
                            kwargs[
                                "task"
                            ].task_id
                        ),
                        specialist_id=slug,
                        status=(
                            SpecialistTaskStatus
                            .COMPLETED
                        ),
                        summary=(
                            f"{slug} complete"
                        ),
                        confidence=0.8,
                    )
                ),
                investigation_actions_used=(
                    used
                ),
                actions_executed=used,
            )

        finally:
            self.active -= 1


def decision(
    slugs=(
        "linux-cpu",
        "linux-memory",
    ),
):
    matches = tuple(
        SpecialistRoutingMatch(
            specialist_id=index,
            specialist_slug=slug,
            specialist_name=slug,
            score=10,
            matched_domains=(slug,),
            matched_trigger_hints=(),
            matched_issue_indexes=(
                index - 1,
            ),
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
        detected_domains=tuple(slugs),
        candidate_specialists=matches,
        selected_specialists=matches,
        unmatched_issue_indexes=(),
        registry_size=len(matches),
        candidate_limit=12,
        selection_limit=4,
    )


def definitions():
    return (
        specialist(
            "linux-cpu",
            identifier=1,
        ),
        specialist(
            "linux-memory",
            identifier=2,
        ),
    )


def test_workers_execute_in_parallel():
    loop = ParallelLoop()

    coordinator = (
        LangGraphServerCoordinator(
            specialist_registry=(
                Registry(
                    definitions()
                )
            ),
            specialist_loop=loop,
            max_concurrency=2,
        )
    )

    output = asyncio.run(
        coordinator.run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=(
                decision()
            ),
            budget=(
                InvestigationBudget(
                    max_specialists=2,
                    max_rounds=3,
                    max_actions=4,
                )
            ),
        )
    )

    assert loop.max_active >= 2
    assert len(output.runs) == 2
    assert (
        output.state.metadata[
            "execution_mode"
        ]
        == "parallel"
    )


def test_global_budget_is_partitioned_safely():
    loop = ParallelLoop(
        consume_full_quota=True
    )

    coordinator = (
        LangGraphServerCoordinator(
            specialist_registry=(
                Registry(
                    definitions()
                )
            ),
            specialist_loop=loop,
            max_concurrency=2,
        )
    )

    output = asyncio.run(
        coordinator.run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=(
                decision()
            ),
            budget=(
                InvestigationBudget(
                    max_specialists=2,
                    max_rounds=3,
                    max_actions=5,
                )
            ),
        )
    )

    quotas = [
        call[
            "investigation_budget"
        ].max_actions
        for call in loop.calls
    ]

    assert sorted(
        quotas
    ) == [2, 3]

    assert sum(quotas) == 5
    assert (
        output
        .investigation_actions_used
        == 5
    )


def test_aggregation_order_follows_routing_order():
    loop = ParallelLoop(
        delays={
            "linux-cpu": 0.06,
            "linux-memory": 0.01,
        }
    )

    coordinator = (
        LangGraphServerCoordinator(
            specialist_registry=(
                Registry(
                    definitions()
                )
            ),
            specialist_loop=loop,
            max_concurrency=2,
        )
    )

    output = asyncio.run(
        coordinator.run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=(
                decision()
            ),
        )
    )

    assert [
        item.specialist_slug
        for item in output.runs
    ] == [
        "linux-cpu",
        "linux-memory",
    ]


def test_parallel_failure_is_isolated():
    loop = ParallelLoop(
        failures=(
            "linux-memory",
        )
    )

    coordinator = (
        LangGraphServerCoordinator(
            specialist_registry=(
                Registry(
                    definitions()
                )
            ),
            specialist_loop=loop,
            max_concurrency=2,
        )
    )

    output = asyncio.run(
        coordinator.run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=(
                decision()
            ),
        )
    )

    statuses = {
        item.specialist_slug:
        item.result.status
        for item
        in output.runs
    }

    assert (
        statuses["linux-cpu"]
        == SpecialistTaskStatus
        .COMPLETED
    )
    assert (
        statuses["linux-memory"]
        == SpecialistTaskStatus
        .FAILED
    )

    assert (
        output.state.status.value
        == "completed"
    )


def test_no_investigation_routes_directly_to_aggregate():
    loop = ParallelLoop()

    coordinator = (
        LangGraphServerCoordinator(
            specialist_registry=(
                Registry(
                    definitions()
                )
            ),
            specialist_loop=loop,
        )
    )

    no_action = (
        InvestigationRoutingDecision(
            should_investigate=False,
            reasons=(),
            detected_domains=(),
            candidate_specialists=(),
            selected_specialists=(),
            unmatched_issue_indexes=(),
            registry_size=2,
            candidate_limit=12,
            selection_limit=4,
        )
    )

    output = asyncio.run(
        coordinator.run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=(
                no_action
            ),
        )
    )

    assert output.runs == ()
    assert loop.calls == []
    assert (
        output.state.metadata[
            "coordinator_stop_reason"
        ]
        == "investigation_not_required"
    )


def test_allocator_never_exceeds_total():
    assert (
        LangGraphServerCoordinator
        ._allocate_actions(
            total_actions=2,
            worker_count=4,
        )
        == (1, 1, 0, 0)
    )

    assert (
        sum(
            LangGraphServerCoordinator
            ._allocate_actions(
                total_actions=12,
                worker_count=4,
            )
        )
        == 12
    )
