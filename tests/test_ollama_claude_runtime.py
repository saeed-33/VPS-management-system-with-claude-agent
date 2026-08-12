import asyncio
from pathlib import Path

from app.runtime.claude.models import (
    ClaudeJobStatus,
    ClaudeRuntimeRequest,
    ClaudeRuntimeResult,
    ClaudeStructuredOutput,
)
from app.runtime.claude.native_monitoring import (
    ClaudeNativeMonitoringRunner,
)
from app.runtime.claude.ollama_runtime import (
    OllamaClaudeCommandBuilder,
)


def request() -> ClaudeRuntimeRequest:
    return ClaudeRuntimeRequest(
        job_id="job-1",
        job_type="monitoring_cycle",
        prompt="monitor server 7",
        max_turns=13,
    )


def project_root(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()

    (project / ".mcp.json").write_text(
        '{"mcpServers":{}}',
        encoding="utf-8",
    )

    return project


def test_ollama_builder_uses_supported_headless_launch(
    tmp_path,
):
    project = project_root(tmp_path)

    command = OllamaClaudeCommandBuilder(
        project_root=project,
        model="qwen-test",
    ).build(request())

    argv = command.argv

    assert argv[:7] == (
        "ollama",
        "launch",
        "claude",
        "--model",
        "qwen-test",
        "--yes",
        "--",
    )

    assert (
        argv[argv.index("--agent") + 1]
        == "server-supervisor"
    )

    assert (
        argv[
            argv.index("--permission-mode") + 1
        ]
        == "dontAsk"
    )

    assert "--strict-mcp-config" in argv
    assert (
        argv[
            argv.index("--output-format") + 1
        ]
        == "json"
    )
    assert (
        argv[
            argv.index("--max-turns") + 1
        ]
        == "13"
    )

    assert argv[-2] == "-p"
    assert argv[-1] == "monitor server 7"
    assert command.cwd == project.resolve()


def test_ollama_builder_avoids_provider_structured_output_extension(
    tmp_path,
):
    project = project_root(tmp_path)

    command = OllamaClaudeCommandBuilder(
        project_root=project,
        model="qwen-test",
    ).build(request())

    assert "--json-schema" not in command.argv


def test_builder_sets_runtime_hook_markers(
    tmp_path,
):
    project = project_root(tmp_path)

    command = OllamaClaudeCommandBuilder(
        project_root=project,
        model="qwen-test",
    ).build(request())

    assert (
        command.env["AI_VPS_LLM_PROVIDER"]
        == "ollama"
    )
    assert (
        command.env["AI_VPS_CLAUDE_RUNTIME"]
        == "1"
    )
    assert (
        command.env[
            "AI_VPS_CLAUDE_RUNTIME_AGENT"
        ]
        == "server-supervisor"
    )
    assert (
        command.env[
            "CLAUDE_CODE_DISABLE_BACKGROUND_TASKS"
        ]
        == "1"
    )


class FakeJobService:
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
            (request, server_id)
        )

    def mark_running(
        self,
        *,
        job_id,
        session_id=None,
    ):
        self.running.append(
            (job_id, session_id)
        )

    def complete_from_result(
        self,
        result,
    ):
        self.completed.append(
            result
        )


class FakeAdapter:
    def __init__(
        self,
        result_factory,
    ):
        self.requests = []
        self._result_factory = (
            result_factory
        )

    async def execute(
        self,
        request,
    ):
        self.requests.append(request)

        return self._result_factory(
            request
        )


def completed_result(request):
    return ClaudeRuntimeResult(
        job_id=request.job_id,
        job_type=request.job_type,
        status=ClaudeJobStatus.COMPLETED,
        session_id="session-1",
        structured_output=ClaudeStructuredOutput(
            status=ClaudeJobStatus.COMPLETED,
            summary="done",
            data={
                "server_id": 7,
            },
        ),
    )


def failed_result(request):
    return ClaudeRuntimeResult(
        job_id=request.job_id,
        job_type=request.job_type,
        status=ClaudeJobStatus.FAILED,
        error_code="runtime_error",
        error_message="provider unavailable",
    )


def test_native_monitoring_runner_persists_job_lifecycle():
    jobs = FakeJobService()

    runner = ClaudeNativeMonitoringRunner(
        runtime_adapter=FakeAdapter(
            completed_result
        ),
        agent_job_service=jobs,
        timeout_seconds=300,
        max_turns=20,
    )

    result = asyncio.run(
        runner.run(7)
    )

    assert (
        result.status
        == ClaudeJobStatus.COMPLETED
    )

    runtime_request, server_id = (
        jobs.created[0]
    )

    assert server_id == 7
    assert (
        runtime_request.context
        == {"server_id": 7}
    )
    assert (
        runtime_request.max_turns
        == 20
    )
    assert (
        runtime_request.timeout_seconds
        == 300
    )
    assert (
        "server_id=7"
        in runtime_request.prompt
    )
    assert (
        "only one valid JSON object"
        in runtime_request.prompt
    )
    assert len(jobs.running) == 1
    assert len(jobs.completed) == 1


def test_native_monitoring_runner_surfaces_failed_runtime():
    jobs = FakeJobService()

    runner = ClaudeNativeMonitoringRunner(
        runtime_adapter=FakeAdapter(
            failed_result
        ),
        agent_job_service=jobs,
        timeout_seconds=300,
        max_turns=20,
    )

    try:
        asyncio.run(
            runner.run(7)
        )
    except Exception as exc:
        assert (
            "provider unavailable"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected scheduler-visible "
            "runtime failure."
        )

    assert len(jobs.completed) == 1


def test_bootstrap_contains_feature_flagged_native_switch():
    root = Path(__file__).resolve().parents[1]

    text = (
        root / "app/bootstrap.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "if settings.claude_runtime_enabled:"
        in text
    )
    assert (
        "OllamaClaudeCommandBuilder("
        in text
    )
    assert (
        "SubprocessClaudeSessionRunner("
        in text
    )
    assert (
        "ClaudeNativeMonitoringRunner("
        in text
    )
    assert (
        "operational_tools_enabled=True"
        in text
    )


def test_runtime_hook_can_detect_env_marked_main_session(
    monkeypatch,
):
    from tools.claude_hooks import (
        runtime_hooks,
    )

    monkeypatch.setenv(
        "AI_VPS_CLAUDE_RUNTIME",
        "1",
    )
    monkeypatch.setenv(
        "AI_VPS_CLAUDE_RUNTIME_AGENT",
        "server-supervisor",
    )

    assert (
        runtime_hooks._is_main_runtime(
            {}
        )
        is True
    )
