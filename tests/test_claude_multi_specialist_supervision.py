import asyncio

from app.runtime.claude import (
    ClaudeJobStatus,
    ClaudeMultiSpecialistSupervisor,
)
from app.mcp import ProjectToolResult


class JobService:
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
            {
                "request": request,
                "server_id": server_id,
            }
        )

    def mark_running(
        self,
        *,
        job_id,
        session_id=None,
    ):
        self.running.append(
            {
                "job_id": job_id,
                "session_id": session_id,
            }
        )

    def complete_from_result(
        self,
        result,
    ):
        self.completed.append(result)


class ToolBoundary:
    def __init__(
        self,
        *,
        selected=("linux-cpu", "postgres"),
        fail_tool=None,
    ):
        self.selected = tuple(selected)
        self.fail_tool = fail_tool
        self.calls = []

    async def execute(
        self,
        call,
    ):
        self.calls.append(
            {
                "tool_id": call.tool_id,
                "arguments": call.arguments,
            }
        )

        if call.tool_id == self.fail_tool:
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=False,
                error_code="forced_failure",
                error_message="Forced failure.",
            )

        if call.tool_id == "get_investigation":
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=True,
                data={
                    "investigation": {
                        "investigation_id": "inv-1",
                        "max_specialists": 4,
                        "candidates": [
                            {
                                "specialist_slug": slug,
                                "is_selected": True,
                                "selected_rank": index,
                            }
                            for index, slug in enumerate(
                                self.selected,
                                start=1,
                            )
                        ],
                    }
                },
            )

        if call.tool_id == "get_specialist_definition":
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=True,
                data={
                    "specialist": {
                        "slug": call.arguments[
                            "specialist_slug"
                        ],
                        "allowed_tool_ids": [
                            "ssh.read_only"
                        ],
                        "max_rounds": 2,
                        "max_actions": 3,
                    }
                },
            )

        if call.tool_id == "run_specialist":
            slug = call.arguments[
                "specialist_slug"
            ]
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=True,
                data={
                    "result": {
                        "final_result": {
                            "task_id": f"inv-1:{slug}:1",
                            "specialist_id": slug,
                            "status": "completed",
                            "summary": (
                                f"{slug} completed."
                            ),
                            "confidence": 0.75,
                            "evidence_ids": [
                                f"ev-{slug}"
                            ],
                        }
                    }
                },
            )

        return ProjectToolResult(
            tool_id=call.tool_id,
            success=False,
            error_code="unknown_tool",
            error_message="Unknown tool.",
        )


def run_supervisor(
    *,
    boundary=None,
    job_service=None,
    **kwargs,
):
    return asyncio.run(
        ClaudeMultiSpecialistSupervisor(
            tool_boundary=(
                boundary
                if boundary is not None
                else ToolBoundary()
            ),
            agent_job_service=(
                job_service
                if job_service is not None
                else JobService()
            ),
        ).run(
            investigation_id="inv-1",
            objective="Deep specialist analysis.",
            job_id="job-1",
            **kwargs,
        )
    )


def test_multi_specialist_supervision_runs_selected_specialists_sequentially():
    boundary = ToolBoundary()
    jobs = JobService()

    result = run_supervisor(
        boundary=boundary,
        job_service=jobs,
    )

    assert result.status == ClaudeJobStatus.COMPLETED
    assert [
        item.specialist_slug
        for item in result.specialist_runs
    ] == ["linux-cpu", "postgres"]
    assert [
        call["tool_id"]
        for call in boundary.calls
    ] == [
        "get_investigation",
        "get_specialist_definition",
        "run_specialist",
        "get_specialist_definition",
        "run_specialist",
    ]
    assert jobs.created[0]["request"].allowed_tools == (
        "get_investigation",
        "get_specialist_definition",
        "run_specialist",
    )
    assert jobs.completed[0].status == (
        ClaudeJobStatus.COMPLETED
    )
    assert jobs.completed[0].tool_call_count == 5


def test_multi_specialist_supervision_respects_max_specialists():
    boundary = ToolBoundary(
        selected=(
            "linux-cpu",
            "postgres",
            "network",
        )
    )

    result = run_supervisor(
        boundary=boundary,
        max_specialists=2,
    )

    assert result.status == ClaudeJobStatus.COMPLETED
    assert [
        item.specialist_slug
        for item in result.specialist_runs
    ] == ["linux-cpu", "postgres"]
    assert [
        call["arguments"].get(
            "specialist_slug"
        )
        for call in boundary.calls
        if call["tool_id"] == "run_specialist"
    ] == ["linux-cpu", "postgres"]


def test_multi_specialist_supervision_fails_when_tool_budget_is_exceeded():
    result = run_supervisor(
        max_tool_calls=2,
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert (
        result.error_code
        == "tool_call_budget_exceeded"
    )
    assert [
        item.tool_id
        for item in result.tool_results
    ] == [
        "get_investigation",
        "get_specialist_definition",
        "run_specialist",
    ]


def test_multi_specialist_supervision_stops_on_tool_failure():
    boundary = ToolBoundary(
        fail_tool="run_specialist",
    )
    jobs = JobService()

    result = run_supervisor(
        boundary=boundary,
        job_service=jobs,
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert result.error_code == "forced_failure"
    assert result.specialist_runs == ()
    assert jobs.completed[0].status == (
        ClaudeJobStatus.FAILED
    )


def test_multi_specialist_supervision_completes_when_none_selected():
    result = run_supervisor(
        boundary=ToolBoundary(
            selected=()
        )
    )

    assert result.status == ClaudeJobStatus.COMPLETED
    assert result.specialist_runs == ()
    assert [
        item.tool_id
        for item in result.tool_results
    ] == ["get_investigation"]
