import asyncio

from app.runtime.claude import (
    ClaudeJobStatus,
    ClaudeSupervisedMonitoringCycle,
)
from app.mcp import ProjectToolResult


class ToolBoundary:
    def __init__(
        self,
        *,
        failures=None,
        profile_id=5,
    ):
        self.calls = []
        self.failures = failures or {}
        self.profile_id = profile_id

    async def execute(
        self,
        call,
    ):
        self.calls.append(
            call
        )

        if call.tool_id in self.failures:
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=False,
                error_code=(
                    self.failures[call.tool_id]
                ),
                error_message=(
                    f"{call.tool_id} failed"
                ),
            )

        if call.tool_id == "get_server_context":
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=True,
                data={
                    "server": {
                        "id": 1,
                        "monitoring_profile_id": (
                            self.profile_id
                        ),
                    }
                },
            )

        if call.tool_id == "get_monitoring_profile":
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=True,
                data={
                    "profile": {
                        "id": call.arguments[
                            "profile_id"
                        ],
                        "commands": [],
                    }
                },
            )

        if call.tool_id == "run_monitoring":
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=True,
                data={
                    "monitoring_report": {
                        "status": "success",
                    }
                },
            )

        if call.tool_id == "get_latest_report":
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=True,
                data={
                    "report": {
                        "id": 77,
                        "status": "success",
                    }
                },
            )

        return ProjectToolResult(
            tool_id=call.tool_id,
            success=False,
            error_code="unknown_tool",
            error_message="unknown tool",
        )


class AgentJobService:
    def __init__(self):
        self.created = []
        self.running = []
        self.completed = []

    def create_from_request(
        self,
        request,
        *,
        server_id=None,
    ):
        self.created.append(
            (
                request,
                server_id,
            )
        )

    def mark_running(
        self,
        *,
        job_id,
        session_id=None,
    ):
        self.running.append(
            (
                job_id,
                session_id,
            )
        )

    def complete_from_result(
        self,
        result,
    ):
        self.completed.append(
            result
        )


def run_cycle(
    *,
    tool_boundary=None,
    job_service=None,
):
    service = ClaudeSupervisedMonitoringCycle(
        tool_boundary=(
            tool_boundary
            if tool_boundary is not None
            else ToolBoundary()
        ),
        agent_job_service=(
            job_service
            if job_service is not None
            else AgentJobService()
        ),
    )
    return asyncio.run(
        service.run(
            server_id=1,
            job_id="job-c5",
        )
    )


def test_cycle_executes_fixed_tool_sequence():
    tools = ToolBoundary()
    jobs = AgentJobService()

    result = run_cycle(
        tool_boundary=tools,
        job_service=jobs,
    )

    assert result.status == ClaudeJobStatus.COMPLETED
    assert result.report_id == 77
    assert [
        call.tool_id
        for call in tools.calls
    ] == [
        "get_server_context",
        "get_monitoring_profile",
        "run_monitoring",
        "get_latest_report",
    ]
    assert (
        tools.calls[1].arguments["profile_id"]
        == 5
    )


def test_cycle_persists_successful_job_observability():
    jobs = AgentJobService()

    result = run_cycle(
        job_service=jobs
    )

    assert jobs.created[0][0].job_id == "job-c5"
    assert jobs.created[0][0].job_type == (
        "claude_supervised_monitoring_cycle"
    )
    assert jobs.created[0][1] == 1
    assert jobs.running[0][0] == "job-c5"

    completed = jobs.completed[0]
    assert completed.status == ClaudeJobStatus.COMPLETED
    assert completed.tool_call_count == 4
    assert (
        completed.usage_metadata["llm_provider"]
        == "ollama"
    )
    assert result.tool_results[-1].tool_id == (
        "get_latest_report"
    )


def test_cycle_stops_and_persists_failure_when_tool_fails():
    tools = ToolBoundary(
        failures={
            "run_monitoring": (
                "monitoring_failed"
            )
        }
    )
    jobs = AgentJobService()

    result = run_cycle(
        tool_boundary=tools,
        job_service=jobs,
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert result.error_code == "monitoring_failed"
    assert [
        call.tool_id
        for call in tools.calls
    ] == [
        "get_server_context",
        "get_monitoring_profile",
        "run_monitoring",
    ]

    completed = jobs.completed[0]
    assert completed.status == ClaudeJobStatus.FAILED
    assert completed.error_code == "monitoring_failed"
    assert completed.tool_call_count == 3


def test_cycle_fails_when_server_has_no_profile():
    tools = ToolBoundary(
        profile_id=None
    )
    jobs = AgentJobService()

    result = run_cycle(
        tool_boundary=tools,
        job_service=jobs,
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert result.error_code == "missing_profile"
    assert [
        call.tool_id
        for call in tools.calls
    ] == [
        "get_server_context",
    ]
    assert len(result.tool_results) == 2


def test_cycle_rejects_invalid_server_id():
    service = ClaudeSupervisedMonitoringCycle(
        tool_boundary=ToolBoundary(),
        agent_job_service=AgentJobService(),
    )

    try:
        asyncio.run(
            service.run(
                server_id=0,
                job_id="job-invalid",
            )
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "server_id must be >= 1."
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )
