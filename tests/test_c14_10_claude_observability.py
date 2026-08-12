from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from app.runtime.claude.observability import (
    ClaudeAgentObservabilityService,
)


class FakeRepository:
    def __init__(self, items) -> None:
        self.items = list(items)

    def get_by_job_id(self, job_id: str):
        return next(
            (
                item
                for item in self.items
                if item.job_id == job_id
            ),
            None,
        )

    def list_recent(
        self,
        *,
        limit=100,
        server_id=None,
        status=None,
    ):
        items = self.items

        if server_id is not None:
            items = [
                item
                for item in items
                if item.server_id == server_id
            ]

        if status is not None:
            items = [
                item
                for item in items
                if item.status == status
            ]

        return items[:limit]


def make_job(
    *,
    job_id="job-1",
    status="completed",
    tools=None,
    mcp_status="connected",
    duration_ms=1200,
):
    started_at = datetime(
        2026,
        8,
        13,
        tzinfo=UTC,
    )

    tools = list(tools or ())

    return SimpleNamespace(
        job_id=job_id,
        job_type="monitoring_cycle",
        server_id=2,
        status=status,
        claude_session_id="session-1",
        created_at=started_at,
        started_at=started_at,
        completed_at=(
            started_at
            + timedelta(milliseconds=duration_ms)
        ),
        turn_count=8,
        tool_call_count=len(tools),
        usage_metadata={
            "duration_ms": duration_ms,
            "duration_api_ms": duration_ms - 100,
            "input_tokens": 1000,
            "output_tokens": 200,
            "total_cost_usd": 0.01,
            "subtype": "success",
            "stop_reason": "end_turn",
            "is_error": False,
            "event_tool_names": tools,
            "event_mcp_servers": [
                {
                    "name": "vps",
                    "status": mcp_status,
                }
            ],
            "modelUsage": {
                "gemma-test": {
                    "inputTokens": 1000,
                    "outputTokens": 200,
                }
            },
        },
        job_metadata={
            "runtime": "claude_code",
            "provider": "ollama",
            "agent": "server-supervisor",
            "max_turns": 20,
            "allowed_tools": [
                "mcp__vps__run_monitoring",
            ],
        },
        error_code=None,
        error_message=None,
    )


def test_trace_normalizes_runtime_evidence():
    job = make_job(
        tools=[
            "mcp__vps__get_server_context",
            "mcp__vps__run_monitoring",
            "mcp__vps__analyze_report",
            "mcp__vps__start_investigation",
            "mcp__vps__run_specialist",
        ]
    )

    service = ClaudeAgentObservabilityService(
        FakeRepository([job])
    )

    trace = service.get_trace("job-1")

    assert trace is not None
    assert trace["required_tools_verified"] is True
    assert trace["mcp_connected"] is True
    assert trace["investigation_started"] is True
    assert trace["specialist_delegation_count"] == 1
    assert trace["duration_ms"] == 1200
    assert trace["input_tokens"] == 1000


def test_summary_exposes_failures_tools_and_mcp_health():
    completed = make_job(
        job_id="job-ok",
        tools=[
            "mcp__vps__run_monitoring",
            "mcp__vps__analyze_report",
            "mcp__vps__run_specialist",
        ],
    )
    failed = make_job(
        job_id="job-failed",
        status="failed",
        tools=[
            "mcp__vps__run_monitoring",
        ],
        mcp_status="failed",
        duration_ms=800,
    )

    service = ClaudeAgentObservabilityService(
        FakeRepository(
            [completed, failed]
        )
    )

    summary = service.summarize_recent()

    assert summary["sample_size"] == 2
    assert summary["completed_count"] == 1
    assert summary["failed_count"] == 1
    assert summary["success_rate"] == 0.5
    assert summary["mcp_disconnected_job_count"] == 1
    assert summary["specialist_delegation_count"] == 1


def test_completed_job_missing_required_tools_is_visible():
    job = make_job(
        tools=[
            "mcp__vps__run_monitoring",
        ]
    )

    service = ClaudeAgentObservabilityService(
        FakeRepository([job])
    )

    summary = service.summarize_recent()

    assert (
        summary[
            "required_tool_verification_failure_count"
        ]
        == 1
    )


def test_missing_job_returns_none():
    service = ClaudeAgentObservabilityService(
        FakeRepository([])
    )

    assert service.get_trace("missing") is None
