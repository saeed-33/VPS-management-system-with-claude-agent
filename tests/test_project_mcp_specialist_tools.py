import asyncio

from app.domain.investigation.contracts import (
    EvidenceKind,
    EvidenceReference,
    SpecialistResult,
    SpecialistTaskStatus,
)
from app.domain.investigation.specialist_investigation_loop import (
    SpecialistInvestigationLoopResult,
    SpecialistLoopStopReason,
)
from app.domain.investigation.specialist_registry import (
    SpecialistRegistrySnapshot,
    SpecialistRuntimeDefinition,
)
from app.mcp import (
    ProjectMcpToolBoundary,
    ProjectToolCall,
)

from tests.test_project_mcp_analysis_tools import (
    AnalysisRepository,
)
from tests.test_project_mcp_investigation_tools import (
    ReadService,
)
from tests.test_project_mcp_tool_boundary import (
    MonitoringService,
    ProfileService,
    ReportService,
    ServerService,
)


def specialist(
    *,
    slug="linux-cpu",
    allowed_tool_ids=("ssh.read_only",),
    max_rounds=2,
    max_actions=3,
):
    return SpecialistRuntimeDefinition(
        id=1,
        slug=slug,
        name="Linux CPU",
        description="CPU diagnostics",
        instructions="Investigate CPU pressure.",
        domains=("cpu",),
        trigger_hints=("high cpu",),
        knowledge_topics=("linux", "cpu"),
        allowed_tool_ids=allowed_tool_ids,
        priority=10,
        max_rounds=max_rounds,
        max_actions=max_actions,
        metadata={"owner": "admin"},
    )


class SpecialistRegistry:
    def __init__(self, definitions):
        self.definitions = tuple(definitions)

    def snapshot(self):
        return SpecialistRegistrySnapshot.build(
            self.definitions
        )


class SpecialistLoop:
    def __init__(self):
        self.calls = []

    async def run(self, **kwargs):
        self.calls.append(kwargs)
        task = kwargs["task"]
        return SpecialistInvestigationLoopResult(
            final_result=SpecialistResult(
                task_id=task.task_id,
                specialist_id=task.specialist_id,
                status=SpecialistTaskStatus.COMPLETED,
                summary="CPU contention confirmed.",
                confidence=0.8,
                evidence_ids=("ev-1",),
            ),
            evidence=(
                EvidenceReference(
                    evidence_id="ev-1",
                    kind=EvidenceKind.COMMAND_RESULT,
                    title="top output",
                ),
            ),
            rounds_completed=1,
            actions_executed=1,
            investigation_actions_used=1,
            stop_reason=SpecialistLoopStopReason.COMPLETED,
            provider="ollama",
            model="qwen3:8b",
            traces=(),
        )


def boundary(
    *,
    registry=None,
    loop=None,
    read=None,
    analysis_repository=None,
):
    return ProjectMcpToolBoundary(
        server_service=ServerService(),
        monitoring_profile_service=(
            ProfileService()
        ),
        monitoring_service=MonitoringService(),
        report_query_service=ReportService(),
        analysis_repository=(
            analysis_repository
            if analysis_repository is not None
            else AnalysisRepository()
        ),
        investigation_read_service=(
            read if read is not None else ReadService()
        ),
        specialist_registry=(
            registry
            if registry is not None
            else SpecialistRegistry([specialist()])
        ),
        specialist_investigation_loop=loop,
    )


def run_tool(
    tool_id,
    arguments,
    *,
    tool_boundary=None,
):
    return asyncio.run(
        (
            tool_boundary
            if tool_boundary is not None
            else boundary()
        ).execute(
            ProjectToolCall(
                tool_id=tool_id,
                arguments=arguments,
            )
        )
    )


def test_get_available_specialists_reads_enabled_runtime_registry():
    result = run_tool(
        "get_available_specialists",
        {
            "domains": ["cpu"],
        },
    )

    assert result.success is True
    assert result.data["specialists"][0]["slug"] == "linux-cpu"
    assert result.data["specialists"][0][
        "allowed_tool_ids"
    ] == ["ssh.read_only"]


def test_get_specialist_definition_reads_latest_registry_snapshot():
    dynamic = SpecialistRegistry(
        [
            specialist(
                allowed_tool_ids=("journalctl.read",),
                max_rounds=1,
                max_actions=0,
            )
        ]
    )

    result = run_tool(
        "get_specialist_definition",
        {
            "specialist_slug": "linux-cpu",
        },
        tool_boundary=boundary(
            registry=dynamic,
        ),
    )

    assert result.success is True
    assert result.data["specialist"][
        "allowed_tool_ids"
    ] == ["journalctl.read"]
    assert result.data["specialist"]["max_actions"] == 0


def test_run_specialist_uses_selected_db_definition_and_budget():
    loop = SpecialistLoop()
    selected = specialist(
        allowed_tool_ids=("ssh.read_only", "journalctl.read"),
        max_rounds=1,
        max_actions=2,
    )

    result = run_tool(
        "run_specialist",
        {
            "investigation_id": "inv-1",
            "specialist_slug": "linux-cpu",
            "objective": "Investigate CPU pressure.",
        },
        tool_boundary=boundary(
            registry=SpecialistRegistry([selected]),
            loop=loop,
        ),
    )

    assert result.success is True
    assert result.data["result"]["provider"] == "ollama"
    assert len(loop.calls) == 1

    call = loop.calls[0]
    assert call["specialist"] is selected
    assert call["specialist"].allowed_tool_ids == (
        "ssh.read_only",
        "journalctl.read",
    )
    assert call[
        "investigation_budget"
    ].max_rounds == 3
    assert call[
        "investigation_budget"
    ].max_actions == 12
    assert call["task"].status == (
        SpecialistTaskStatus.RUNNING
    )
    assert call["task"].knowledge_topics == (
        "linux",
        "cpu",
    )
    assert call["initial_analysis_issues"] == (
        {
            "title": "High CPU",
        },
    )


def test_run_specialist_rejects_unselected_specialist():
    loop = SpecialistLoop()

    result = run_tool(
        "run_specialist",
        {
            "investigation_id": "inv-1",
            "specialist_slug": "network",
            "objective": "Investigate network.",
        },
        tool_boundary=boundary(
            registry=SpecialistRegistry(
                [
                    specialist(
                        slug="network",
                    )
                ]
            ),
            loop=loop,
        ),
    )

    assert result.success is False
    assert result.error_code == "specialist_not_selected"
    assert loop.calls == []


def test_run_specialist_requires_configured_loop():
    result = run_tool(
        "run_specialist",
        {
            "investigation_id": "inv-1",
            "specialist_slug": "linux-cpu",
            "objective": "Investigate CPU pressure.",
        },
    )

    assert result.success is False
    assert result.error_code == "validation_error"
    assert (
        "specialist_investigation_loop"
        in result.error_message
    )
