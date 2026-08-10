import asyncio
from dataclasses import dataclass

from app.agent.investigation.contracts import (
    InvestigationBudget,
    SpecialistResult,
    SpecialistTaskStatus,
)
from app.agent.investigation.investigation_router import (
    InvestigationRoutingDecision,
    SpecialistRoutingMatch,
)
from payload.app.agent.investigation.server_coordinator import ServerCoordinator
from app.agent.investigation.specialist_registry import (
    SpecialistRegistrySnapshot,
    SpecialistRuntimeDefinition,
)


def specialist(slug):
    return SpecialistRuntimeDefinition(
        id=1 if slug == "linux-cpu" else 2,
        slug=slug,
        name=slug,
        description=None,
        instructions=None,
        domains=("cpu",) if slug == "linux-cpu" else ("memory",),
        trigger_hints=(),
        knowledge_topics=(),
        allowed_tool_ids=(),
        priority=10,
        max_rounds=3,
        max_actions=5,
        metadata={},
    )


class Registry:
    def __init__(self, definitions):
        self._snapshot = SpecialistRegistrySnapshot.build(definitions)

    def snapshot(self):
        return self._snapshot


@dataclass
class LoopOutput:
    final_result: SpecialistResult
    evidence: tuple = ()
    investigation_actions_used: int = 0


class Loop:
    def __init__(self, fail_slug=None):
        self.calls = []
        self.fail_slug = fail_slug

    async def run(self, **kwargs):
        definition = kwargs["specialist"]
        self.calls.append(kwargs)
        if definition.slug == self.fail_slug:
            raise RuntimeError("boom")
        return LoopOutput(
            final_result=SpecialistResult(
                task_id=kwargs["task"].task_id,
                specialist_id=definition.slug,
                status=SpecialistTaskStatus.COMPLETED,
                summary=f"{definition.slug} complete",
                confidence=0.8,
            ),
            investigation_actions_used=(
                kwargs["investigation_actions_used"] + 1
            ),
        )


def decision(slugs=("linux-cpu", "linux-memory")):
    matches = tuple(
        SpecialistRoutingMatch(
            specialist_id=index,
            specialist_slug=slug,
            specialist_name=slug,
            score=10,
            matched_domains=(
                ("cpu",) if slug == "linux-cpu" else ("memory",)
            ),
            matched_trigger_hints=(),
            matched_issue_indexes=(index - 1,),
            priority=10,
        )
        for index, slug in enumerate(slugs, start=1)
    )
    return InvestigationRoutingDecision(
        should_investigate=True,
        reasons=(),
        detected_domains=("cpu", "memory"),
        candidate_specialists=matches,
        selected_specialists=matches,
        unmatched_issue_indexes=(),
        registry_size=2,
        candidate_limit=12,
        selection_limit=4,
    )


def test_cpu_and_memory_results_are_collected():
    definitions = (specialist("linux-cpu"), specialist("linux-memory"))
    loop = Loop()
    output = asyncio.run(
        ServerCoordinator(
            specialist_registry=Registry(definitions),
            specialist_loop=loop,
        ).run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=decision(),
            budget=InvestigationBudget(
                max_specialists=4,
                max_rounds=3,
                max_actions=12,
            ),
            registry_snapshot=SpecialistRegistrySnapshot.build(definitions),
        )
    )
    assert len(output.state.results) == 2
    assert output.investigation_actions_used == 2
    assert loop.calls[0]["investigation_actions_used"] == 0
    assert loop.calls[1]["investigation_actions_used"] == 1


def test_partial_specialist_failure_preserves_success():
    definitions = (specialist("linux-cpu"), specialist("linux-memory"))
    output = asyncio.run(
        ServerCoordinator(
            specialist_registry=Registry(definitions),
            specialist_loop=Loop(fail_slug="linux-memory"),
        ).run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=decision(),
            registry_snapshot=SpecialistRegistrySnapshot.build(definitions),
        )
    )
    statuses = {item.specialist_id: item.status for item in output.state.results}
    assert statuses["linux-cpu"] == SpecialistTaskStatus.COMPLETED
    assert statuses["linux-memory"] == SpecialistTaskStatus.FAILED
    assert output.state.status.value == "completed"


def test_no_selected_specialists_completes_without_loop():
    definitions = (specialist("linux-cpu"),)
    loop = Loop()
    empty = InvestigationRoutingDecision(
        should_investigate=True,
        reasons=(),
        detected_domains=("cpu",),
        candidate_specialists=(),
        selected_specialists=(),
        unmatched_issue_indexes=(0,),
        registry_size=1,
        candidate_limit=12,
        selection_limit=4,
    )
    output = asyncio.run(
        ServerCoordinator(
            specialist_registry=Registry(definitions),
            specialist_loop=loop,
        ).run(
            server_id=2,
            report_id=1,
            analysis_id=1,
            routing_decision=empty,
        )
    )
    assert output.runs == ()
    assert output.state.status.value == "completed"
    assert output.state.metadata["coordinator_stop_reason"] == (
        "no_selected_specialists"
    )
    assert loop.calls == []
