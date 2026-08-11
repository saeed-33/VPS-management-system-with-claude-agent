import asyncio
import json

from app.runtime.claude import (
    ClaudeJobStatus,
    ClaudeRawResult,
    ClaudeRuntimeAdapter,
    ClaudeRuntimeRequest,
)
from app.runtime.claude.exceptions import (
    ClaudeRuntimeError,
)


def request(
    **overrides,
) -> ClaudeRuntimeRequest:
    values = {
        "job_id": "job-1",
        "job_type": "monitoring_cycle",
        "prompt": "Run the fixed workflow.",
        "timeout_seconds": 1.0,
    }
    values.update(overrides)
    return ClaudeRuntimeRequest(
        **values
    )


class Runner:
    def __init__(
        self,
        *,
        content=None,
        delay_seconds=0.0,
        error: Exception | None = None,
    ):
        self.content = (
            content
            if content is not None
            else json.dumps(
                {
                    "status": "completed",
                    "summary": "Cycle complete.",
                    "data": {
                        "report_id": 123,
                    },
                    "metadata": {
                        "mode": "test",
                    },
                }
            )
        )
        self.delay_seconds = delay_seconds
        self.error = error
        self.cancelled_sessions = []

    async def run(
        self,
        runtime_request,
    ):
        if self.delay_seconds:
            await asyncio.sleep(
                self.delay_seconds
            )

        if self.error is not None:
            raise self.error

        return ClaudeRawResult(
            session_id="session-1",
            content=self.content,
            turn_count=2,
            tool_call_count=0,
            usage_metadata={
                "tokens": 42,
            },
        )

    async def cancel(
        self,
        session_id,
    ):
        self.cancelled_sessions.append(
            session_id
        )


def test_bounded_claude_invocation_succeeds():
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner()
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.COMPLETED
    assert result.session_id == "session-1"
    assert result.error_code is None
    assert (
        result.structured_output.summary
        == "Cycle complete."
    )
    assert (
        result.structured_output.data["report_id"]
        == 123
    )
    assert result.turn_count == 2
    assert result.tool_call_count == 0
    assert result.usage_metadata["tokens"] == 42


def test_timeout_is_returned_as_controlled_result():
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner(
                delay_seconds=0.05,
            )
        ).execute(
            request(
                timeout_seconds=0.001,
            )
        )
    )

    assert result.status == ClaudeJobStatus.TIMED_OUT
    assert result.error_code == "timed_out"
    assert "exceeded" in result.error_message


def test_runtime_failure_is_returned_as_controlled_result():
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner(
                error=ClaudeRuntimeError(
                    "Claude CLI failed."
                )
            )
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert result.error_code == "runtime_error"
    assert result.error_message == "Claude CLI failed."


def test_invalid_structured_output_is_rejected():
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner(
                content="not json"
            )
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert (
        result.error_code
        == "invalid_structured_output"
    )
    assert result.session_id == "session-1"


def test_operational_tool_access_is_disabled_in_c2():
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner()
        ).execute(
            request(
                allowed_tools=(
                    "run_monitoring",
                )
            )
        )
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert (
        result.error_code
        == "tool_access_disabled"
    )
    assert result.session_id is None


def test_claude_reported_failure_remains_failed():
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner(
                content=json.dumps(
                    {
                        "status": "failed",
                        "summary": "Could not complete.",
                    }
                )
            )
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert (
        result.error_code
        == "claude_reported_failure"
    )
    assert result.error_message == "Could not complete."
