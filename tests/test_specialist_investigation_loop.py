import asyncio
from types import MappingProxyType

from app.core.contracts.investigation import (
    EvidenceKind,
    EvidenceReference,
    InvestigationBudget,
    SpecialistResult,
    SpecialistTask,
    SpecialistTaskStatus,
)
from app.core.policies.diagnostic_policy import (
    DiagnosticPolicyEngine,
)
from app.core.policies.diagnostic_tools import (
    DiagnosticToolCall,
    build_default_diagnostic_tool_registry,
)
from app.capabilities.investigation.specialist_context import (
    SpecialistContextSnapshot,
)
from app.capabilities.investigation.specialist_investigation_loop import (
    SpecialistInvestigationLoop,
    SpecialistLoopStopReason,
)
from app.capabilities.investigation.specialist_reasoning_agent import (
    SpecialistDiagnosticToolRequest,
    SpecialistReasoningExecution,
)
from app.capabilities.investigation.specialist_registry import (
    SpecialistRuntimeDefinition,
)


class ContextBuilder:
    def __init__(self):
        self.calls = []

    async def build(
        self,
        *,
        task,
        specialist,
        detected_domains=(),
        evidence=(),
        initial_analysis_summary=None,
        initial_analysis_issues=(),
        incident_contexts=(),
    ):
        self.calls.append(
            tuple(
                item.evidence_id
                for item in evidence
            )
        )

        return SpecialistContextSnapshot(
            task_id=task.task_id,
            investigation_id=(
                task.investigation_id
            ),
            specialist_slug=(
                specialist.slug
            ),
            specialist_name=(
                specialist.name
            ),
            objective=task.objective,
            instructions=None,
            domains=(
                detected_domains
                or specialist.domains
            ),
            knowledge_query="test",
            initial_analysis_summary=(
                initial_analysis_summary
            ),
            initial_analysis_issues=(
                initial_analysis_issues
            ),
            evidence=tuple(evidence),
            incidents=(),
            knowledge_chunks=(),
            knowledge_sources=(),
            rendered_context="context",
            character_count=7,
        )


class ReasoningAgent:
    def __init__(self, executions):
        self.executions = list(
            executions
        )
        self.catalogs = []

    async def reason(
        self,
        *,
        context,
        allowed_specialist_slugs=(),
        diagnostic_tool_catalog=None,
        force_final_synthesis=False,
    ):
        self.catalogs.append(
            diagnostic_tool_catalog
        )
        return self.executions.pop(0)


class EvidenceCollector:
    def __init__(self):
        self.calls = []

    async def collect(self, request):
        self.calls.append(request)

        return EvidenceReference(
            evidence_id=request.evidence_id,
            kind=(
                EvidenceKind.COMMAND_RESULT
            ),
            title=(
                "Collected "
                + request.policy_result.tool_id
            ),
            source_id=request.server_id,
            excerpt="live evidence",
            metadata={
                "success": True,
            },
        )


def specialist(
    *,
    allowed_tool_ids=(
        "network-listeners",
        "systemd-status",
    ),
    max_rounds=3,
    max_actions=4,
):
    return SpecialistRuntimeDefinition(
        id=1,
        slug="nginx",
        name="Nginx Investigator",
        description=None,
        instructions=None,
        domains=("nginx", "network"),
        trigger_hints=(),
        knowledge_topics=(),
        allowed_tool_ids=(
            allowed_tool_ids
        ),
        priority=10,
        max_rounds=max_rounds,
        max_actions=max_actions,
        metadata=MappingProxyType({}),
    )


def task():
    return SpecialistTask(
        task_id="task-1",
        investigation_id="inv-1",
        server_id=2,
        report_id=1,
        specialist_id="nginx",
        objective="Investigate NGINX.",
    )


def result(
    *,
    summary,
    confidence,
):
    return SpecialistResult(
        task_id="task-1",
        specialist_id="nginx",
        status=(
            SpecialistTaskStatus.COMPLETED
        ),
        summary=summary,
        confidence=confidence,
    )


def execution(
    *,
    summary,
    confidence,
    requests=(),
):
    return SpecialistReasoningExecution(
        result=result(
            summary=summary,
            confidence=confidence,
        ),
        provider="fake",
        model="fake-model",
        diagnostic_tool_requests=tuple(
            requests
        ),
    )


def request_tool(
    tool_id,
    arguments,
):
    return SpecialistDiagnosticToolRequest(
        call=DiagnosticToolCall(
            tool_id=tool_id,
            arguments=arguments,
        ),
        rationale="Need live evidence.",
    )


def make_loop(executions):
    context_builder = ContextBuilder()
    reasoning_agent = ReasoningAgent(
        executions
    )
    collector = EvidenceCollector()
    registry = (
        build_default_diagnostic_tool_registry()
    )

    loop = SpecialistInvestigationLoop(
        context_builder=context_builder,
        reasoning_agent=reasoning_agent,
        diagnostic_tool_registry=registry,
        diagnostic_policy_engine=(
            DiagnosticPolicyEngine(
                registry=registry
            )
        ),
        evidence_collection_service=(
            collector
        ),
    )

    return (
        loop,
        context_builder,
        reasoning_agent,
        collector,
    )


def test_loop_collects_evidence_then_reasons_again():
    first = execution(
        summary="Need listeners.",
        confidence=0.2,
        requests=(
            request_tool(
                "network-listeners",
                {},
            ),
        ),
    )

    second = execution(
        summary="Listener evidence reviewed.",
        confidence=0.8,
        requests=(),
    )

    loop, context_builder, agent, collector = (
        make_loop(
            [first, second]
        )
    )

    output = asyncio.run(
        loop.run(
            task=task(),
            specialist=specialist(),
            investigation_budget=(
                InvestigationBudget(
                    max_specialists=4,
                    max_rounds=3,
                    max_actions=12,
                )
            ),
        )
    )

    assert output.stop_reason == (
        SpecialistLoopStopReason.COMPLETED
    )
    assert output.rounds_completed == 2
    assert output.actions_executed == 1
    assert len(output.evidence) == 1
    assert collector.calls
    assert context_builder.calls == [
        (),
        (
            "task-1:r1:a1:"
            "network-listeners",
        ),
    ]
    assert "network-listeners" in (
        agent.catalogs[0]
    )


def test_denied_request_forces_synthesis_without_execution():
    first = execution(
        summary="Need an unassigned tool.",
        confidence=0.1,
        requests=(
            request_tool(
                "postgres-ready",
                {},
            ),
        ),
    )

    second = execution(
        summary=(
            "Final conclusion from existing evidence; "
            "the requested Tool was unavailable."
        ),
        confidence=0.3,
        requests=(),
    )

    loop, _, _, collector = (
        make_loop([first, second])
    )

    output = asyncio.run(
        loop.run(
            task=task(),
            specialist=specialist(
                allowed_tool_ids=(
                    "network-listeners",
                )
            ),
            investigation_budget=(
                InvestigationBudget()
            ),
        )
    )

    assert output.stop_reason == (
        SpecialistLoopStopReason.COMPLETED
    )
    assert output.rounds_completed == 2
    assert output.actions_executed == 0
    assert collector.calls == []
    assert (
        output
        .traces[0]
        .tool_decisions[0]
        .decision
        == "denied"
    )
    assert output.final_result.summary == (
        "Final conclusion from existing evidence; "
        "the requested Tool was unavailable."
    )


def test_last_round_requests_are_not_executed():
    first = execution(
        summary="Still need evidence.",
        confidence=0.2,
        requests=(
            request_tool(
                "network-listeners",
                {},
            ),
        ),
    )

    synthesis = execution(
        summary=(
            "Final synthesis at the round boundary."
        ),
        confidence=0.4,
        requests=(),
    )

    loop, context_builder, agent, collector = (
        make_loop([first, synthesis])
    )

    output = asyncio.run(
        loop.run(
            task=task(),
            specialist=specialist(
                max_rounds=1
            ),
            investigation_budget=(
                InvestigationBudget(
                    max_rounds=1
                )
            ),
        )
    )

    assert output.stop_reason == (
        SpecialistLoopStopReason
        .MAX_ROUNDS
    )
    assert output.rounds_completed == 1
    assert output.actions_executed == 0
    assert collector.calls == []
    assert output.final_result.summary == (
        "Final synthesis at the round boundary."
    )
    assert context_builder.calls == [(), ()]
    assert agent.catalogs[0] is not None
    assert agent.catalogs[1] is None


def test_action_budget_stops_additional_execution():
    first = execution(
        summary="Need two checks.",
        confidence=0.2,
        requests=(
            request_tool(
                "network-listeners",
                {},
            ),
            request_tool(
                "systemd-status",
                {"service": "nginx"},
            ),
        ),
    )

    synthesis = execution(
        summary=(
            "Final synthesis from evidence collected "
            "before the action budget was exhausted."
        ),
        confidence=0.6,
        requests=(),
    )

    loop, context_builder, agent, collector = (
        make_loop([first, synthesis])
    )

    output = asyncio.run(
        loop.run(
            task=task(),
            specialist=specialist(
                max_actions=1,
            ),
            investigation_budget=(
                InvestigationBudget(
                    max_rounds=3,
                    max_actions=1,
                )
            ),
        )
    )

    assert output.stop_reason == (
        SpecialistLoopStopReason
        .MAX_ACTIONS
    )
    assert output.rounds_completed == 1
    assert output.actions_executed == 1
    assert len(collector.calls) == 1
    assert len(output.evidence) == 1
    assert output.final_result.summary == (
        "Final synthesis from evidence collected "
        "before the action budget was exhausted."
    )
    assert context_builder.calls == [
        (),
        (
            "task-1:r1:a1:"
            "network-listeners",
        ),
    ]
    assert agent.catalogs[0] is not None
    assert agent.catalogs[1] is None


def test_duplicate_request_is_not_executed_twice():
    first = execution(
        summary="Need listeners.",
        confidence=0.2,
        requests=(
            request_tool(
                "network-listeners",
                {},
            ),
        ),
    )

    second = execution(
        summary="Requesting same evidence again.",
        confidence=0.3,
        requests=(
            request_tool(
                "network-listeners",
                {},
            ),
        ),
    )

    third = execution(
        summary="Final conclusion from existing evidence.",
        confidence=0.8,
        requests=(),
    )

    loop, _, _, collector = (
        make_loop(
            [first, second, third]
        )
    )

    output = asyncio.run(
        loop.run(
            task=task(),
            specialist=specialist(),
            investigation_budget=(
                InvestigationBudget()
            ),
        )
    )

    assert output.stop_reason == (
        SpecialistLoopStopReason.COMPLETED
    )
    assert output.rounds_completed == 3
    assert output.actions_executed == 1
    assert len(collector.calls) == 1
    assert (
        output
        .traces[1]
        .tool_decisions[0]
        .reasons
        == ("duplicate_request",)
    )
    assert output.final_result.summary == (
        "Final conclusion from existing evidence."
    )
