from pathlib import Path

from app.runtime.claude.models import ClaudeRuntimeRequest
from app.runtime.claude.ollama_runtime import (
    OllamaClaudeCommandBuilder,
)


def test_direct_claude_uses_ollama_backend(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / ".mcp.json").write_text(
        '{"mcpServers":{}}',
        encoding="utf-8",
    )

    builder = OllamaClaudeCommandBuilder(
        project_root=project,
        model="gemma-test",
        base_url="http://127.0.0.1:11434",
        executable="claude",
    )

    request = ClaudeRuntimeRequest(
        job_id="job-1",
        job_type="monitoring_cycle",
        prompt="monitor server 7",
        max_turns=13,
    )

    command = builder.build(request)
    argv = command.argv
    env = command.env

    assert argv[0] == "claude"
    assert "launch" not in argv
    assert argv[argv.index("--model") + 1] == "gemma-test"
    assert argv[argv.index("--agent") + 1] == "server-supervisor"
    assert argv[argv.index("--output-format") + 1] == "stream-json"
    assert "--verbose" in argv
    assert argv[argv.index("--setting-sources") + 1] == "project"
    assert "--strict-mcp-config" in argv
    assert "--json-schema" not in argv
    assert argv[-2] == "-p"
    assert argv[-1] == "monitor server 7"

    assert env["ANTHROPIC_AUTH_TOKEN"] == "ollama"
    assert env["ANTHROPIC_API_KEY"] == ""
    assert env["ANTHROPIC_BASE_URL"] == "http://127.0.0.1:11434"
    assert env["CLAUDE_CODE_SUBAGENT_MODEL"] == "gemma-test"
    assert env["AI_VPS_LLM_PROVIDER"] == "ollama"


def test_runtime_composition_uses_direct_claude_settings():
    root = Path(__file__).resolve().parents[1]
    text = (
        root
        / "app"
        / "composition"
        / "runtime.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "base_url=settings.ollama_base_url" in text
    assert "settings.claude_runtime_executable" in text

