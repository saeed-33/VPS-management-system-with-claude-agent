import asyncio
import json
import pytest
import sys
from pathlib import Path

from app.runtime.claude import (
    ClaudeJobStatus,
    ClaudeCliJsonDecoder,
    ClaudeProcessCommand,
    ClaudeRuntimeAdapter,
    ClaudeRuntimeRequest,
    SubprocessClaudeSessionRunner,
)
from app.runtime.claude.exceptions import (
    ClaudeProcessExecutionError,
    ClaudeProcessOutputError,
)


def request(
    **overrides,
) -> ClaudeRuntimeRequest:
    values = {
        "job_id": "job-1",
        "job_type": "monitoring_cycle",
        "prompt": "Run one bounded server cycle.",
        "timeout_seconds": 2.0,
    }
    values.update(overrides)
    return ClaudeRuntimeRequest(
        **values
    )


class ScriptCommandBuilder:
    def __init__(
        self,
        script: Path,
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        self._script = script
        self._cwd = cwd
        self._env = env or {}

    def build(
        self,
        runtime_request,
    ) -> ClaudeProcessCommand:
        return ClaudeProcessCommand(
            argv=(
                sys.executable,
                str(self._script),
            ),
            cwd=self._cwd,
            env=self._env,
        )


def write_script(
    tmp_path: Path,
    content: str,
) -> Path:
    path = tmp_path / "child.py"
    path.write_text(
        content,
        encoding="utf-8",
    )
    return path


def test_process_runner_decodes_structured_output(
    tmp_path,
):
    project = tmp_path / "project"
    project.mkdir()

    script = write_script(
        tmp_path,
        """
import json
print(json.dumps({
    "session_id": "session-1",
    "structured_output": {
        "status": "completed",
        "summary": "Cycle complete.",
        "data": {"report_id": 91}
    },
    "num_turns": 4,
    "usage": {
        "input_tokens": 100,
        "output_tokens": 30
    },
    "total_cost_usd": 0.0
}))
""",
    )

    runner = SubprocessClaudeSessionRunner(
        command_builder=ScriptCommandBuilder(
            script
        ),
        project_root=project,
    )

    raw = asyncio.run(
        runner.run(
            request()
        )
    )

    assert raw.session_id == "session-1"
    assert raw.turn_count == 4
    assert raw.tool_call_count == 0
    assert raw.usage_metadata[
        "input_tokens"
    ] == 100
    assert raw.usage_metadata[
        "total_cost_usd"
    ] == 0.0

    content = json.loads(
        raw.content
    )
    assert content["status"] == "completed"
    assert content["data"]["report_id"] == 91


def test_process_runner_accepts_result_text_envelope(
    tmp_path,
):
    project = tmp_path / "project"
    project.mkdir()

    inner = json.dumps(
        {
            "status": "completed",
            "summary": "Done.",
            "data": {},
        }
    )

    script = write_script(
        tmp_path,
        f"""
import json
print(json.dumps({{
    "session_id": "session-result",
    "result": {inner!r}
}}))
""",
    )

    runner = SubprocessClaudeSessionRunner(
        command_builder=ScriptCommandBuilder(
            script
        ),
        project_root=project,
    )

    raw = asyncio.run(
        runner.run(
            request()
        )
    )

    assert raw.content == inner


def test_process_runner_rejects_invalid_json_output(
    tmp_path,
):
    project = tmp_path / "project"
    project.mkdir()

    script = write_script(
        tmp_path,
        'print("not-json")\n',
    )

    runner = SubprocessClaudeSessionRunner(
        command_builder=ScriptCommandBuilder(
            script
        ),
        project_root=project,
    )

    try:
        asyncio.run(
            runner.run(
                request()
            )
        )
    except ClaudeProcessOutputError as exc:
        assert "valid JSON" in str(exc)
    else:
        raise AssertionError(
            "Expected ClaudeProcessOutputError."
        )


def test_process_runner_returns_controlled_nonzero_failure(
    tmp_path,
):
    project = tmp_path / "project"
    project.mkdir()

    script = write_script(
        tmp_path,
        """
import sys
print("launcher failed safely", file=sys.stderr)
raise SystemExit(7)
""",
    )

    runner = SubprocessClaudeSessionRunner(
        command_builder=ScriptCommandBuilder(
            script
        ),
        project_root=project,
    )

    try:
        asyncio.run(
            runner.run(
                request()
            )
        )
    except ClaudeProcessExecutionError as exc:
        message = str(exc)
        assert "code 7" in message
        assert "launcher failed safely" in message
        assert request().prompt not in message
    else:
        raise AssertionError(
            "Expected ClaudeProcessExecutionError."
        )


def test_process_runner_requires_project_root_cwd(
    tmp_path,
):
    project = tmp_path / "project"
    project.mkdir()
    other = tmp_path / "other"
    other.mkdir()

    script = write_script(
        tmp_path,
        'print("{}")\n',
    )

    runner = SubprocessClaudeSessionRunner(
        command_builder=ScriptCommandBuilder(
            script,
            cwd=other,
        ),
        project_root=project,
    )

    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=runner
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert result.error_code == "runtime_error"
    assert "project_root" in result.error_message


def test_adapter_timeout_terminates_active_process(
    tmp_path,
):
    project = tmp_path / "project"
    project.mkdir()

    script = write_script(
        tmp_path,
        """
import time
time.sleep(30)
""",
    )

    runner = SubprocessClaudeSessionRunner(
        command_builder=ScriptCommandBuilder(
            script
        ),
        project_root=project,
        terminate_grace_seconds=0.5,
    )

    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=runner
        ).execute(
            request(
                timeout_seconds=0.05,
            )
        )
    )

    assert result.status == ClaudeJobStatus.TIMED_OUT
    assert result.error_code == "timed_out"
    assert runner.active_job_ids == ()


def test_cancel_by_job_id_terminates_process(
    tmp_path,
):
    project = tmp_path / "project"
    project.mkdir()

    script = write_script(
        tmp_path,
        """
import time
time.sleep(30)
""",
    )

    async def scenario():
        runner = SubprocessClaudeSessionRunner(
            command_builder=ScriptCommandBuilder(
                script
            ),
            project_root=project,
            terminate_grace_seconds=0.5,
        )
        task = asyncio.create_task(
            runner.run(
                request()
            )
        )

        for _ in range(100):
            if runner.active_job_ids:
                break
            await asyncio.sleep(0.01)

        assert runner.active_job_ids == (
            "job-1",
        )

        await runner.cancel(
            "job-1"
        )

        try:
            await task
        except ClaudeProcessExecutionError:
            pass

        assert runner.active_job_ids == ()

    asyncio.run(
        scenario()
    )


def test_command_environment_is_applied_without_prompt_transport(
    tmp_path,
):
    project = tmp_path / "project"
    project.mkdir()

    script = write_script(
        tmp_path,
        """
import json
import os
print(json.dumps({
    "session_id": "session-env",
    "structured_output": {
        "status": "completed",
        "summary": "Environment verified.",
        "data": {
            "provider": os.environ.get("TEST_PROVIDER")
        }
    }
}))
""",
    )

    runner = SubprocessClaudeSessionRunner(
        command_builder=ScriptCommandBuilder(
            script,
            env={
                "TEST_PROVIDER": "test-provider",
            },
        ),
        project_root=project,
    )

    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=runner
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.COMPLETED
    assert result.structured_output.data[
        "provider"
    ] == "test-provider"


def test_decoder_accepts_strict_batched_event_array():
    decoder = ClaudeCliJsonDecoder()

    stdout = json.dumps(
        [
            {
                "type": "system",
                "subtype": "init",
                "session_id": "session-123",
            },
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {
                            "type": "text",
                            "text": "working",
                        }
                    ]
                },
            },
            {
                "type": "result",
                "subtype": "success",
                "session_id": "session-123",
                "num_turns": 2,
                "result": (
                    '{"status":"completed",'
                    '"summary":"done",'
                    '"data":{},'
                    '"metadata":{}}'
                ),
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 5,
                },
            },
        ]
    )

    result = decoder.decode(stdout)

    assert result.session_id == "session-123"
    assert result.turn_count == 2
    assert '"status":"completed"' in result.content
    assert result.usage_metadata["input_tokens"] == 10
    assert result.usage_metadata["subtype"] == "success"


def test_decoder_rejects_event_array_without_final_result():
    decoder = ClaudeCliJsonDecoder()

    stdout = json.dumps(
        [
            {
                "type": "system",
                "subtype": "init",
                "session_id": "session-123",
            },
            {
                "type": "assistant",
            },
        ]
    )

    with pytest.raises(
        ClaudeProcessOutputError,
        match="exactly one result event",
    ):
        decoder.decode(stdout)


def test_decoder_rejects_event_array_session_mismatch():
    decoder = ClaudeCliJsonDecoder()

    stdout = json.dumps(
        [
            {
                "type": "system",
                "subtype": "init",
                "session_id": "session-a",
            },
            {
                "type": "result",
                "subtype": "success",
                "session_id": "session-b",
                "result": (
                    '{"status":"completed",'
                    '"summary":"done",'
                    '"data":{},'
                    '"metadata":{}}'
                ),
            },
        ]
    )

    with pytest.raises(
        ClaudeProcessOutputError,
        match="session_id mismatch",
    ):
        decoder.decode(stdout)


def test_decoder_surfaces_error_max_turns_result():
    decoder = ClaudeCliJsonDecoder()

    stdout = json.dumps(
        [
            {
                "type": "system",
                "subtype": "init",
                "session_id": "session-123",
            },
            {
                "type": "result",
                "subtype": "error_max_turns",
                "session_id": "session-123",
                "num_turns": 20,
                "is_error": True,
                "stop_reason": "tool_use",
            },
        ]
    )

    with pytest.raises(
        ClaudeProcessOutputError,
        match="subtype=error_max_turns",
    ):
        decoder.decode(stdout)


def test_decoder_counts_tool_use_blocks_from_event_array():
    decoder = ClaudeCliJsonDecoder()

    stdout = json.dumps(
        [
            {
                "type": "system",
                "subtype": "init",
                "session_id": "session-123",
            },
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "mcp__vps__get_server_context",
                            "input": {
                                "server_id": 2,
                            },
                        },
                        {
                            "type": "tool_use",
                            "name": "mcp__vps__run_monitoring",
                            "input": {
                                "server_id": 2,
                            },
                        },
                    ]
                },
            },
            {
                "type": "result",
                "subtype": "success",
                "session_id": "session-123",
                "num_turns": 2,
                "result": (
                    '{"status":"completed",'
                    '"summary":"done",'
                    '"data":{},'
                    '"metadata":{}}'
                ),
                "usage": {},
            },
        ]
    )

    result = decoder.decode(stdout)

    assert result.tool_call_count == 2
    assert result.usage_metadata["event_tool_names"] == [
        "mcp__vps__get_server_context",
        "mcp__vps__run_monitoring",
    ]

