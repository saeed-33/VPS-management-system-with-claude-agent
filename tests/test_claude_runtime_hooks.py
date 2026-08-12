import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "tools" / "claude_hooks" / "runtime_hooks.py"


def read_settings() -> dict:
    return json.loads(
        (ROOT / ".claude/settings.json").read_text(
            encoding="utf-8"
        )
    )


def run_hook(
    payload: dict,
    tmp_path: Path,
    *,
    provider: str = "ollama",
):
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(ROOT)
    env["AI_VPS_LLM_PROVIDER"] = provider
    env["AI_VPS_RUNTIME_HOOK_AUDIT_DIR"] = str(
        tmp_path / "events"
    )

    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    output = (
        json.loads(result.stdout)
        if result.stdout.strip()
        else None
    )
    return result, output, Path(
        env["AI_VPS_RUNTIME_HOOK_AUDIT_DIR"]
    )


def runtime_payload(event: str) -> dict:
    return {
        "session_id": "session-test",
        "cwd": str(ROOT),
        "permission_mode": "dontAsk",
        "hook_event_name": event,
        "agent_type": "server-supervisor",
    }


def test_settings_register_only_concrete_runtime_hooks():
    hooks = read_settings()["hooks"]

    assert set(hooks) == {
        "SessionStart",
        "UserPromptSubmit",
        "ConfigChange",
        "SubagentStart",
        "SubagentStop",
        "SessionEnd",
    }

    assert hooks["SessionStart"][0]["matcher"] == (
        "startup|resume"
    )
    assert hooks["ConfigChange"][0]["matcher"] == (
        "project_settings|local_settings|skills"
    )
    assert hooks["SubagentStart"][0]["matcher"] == (
        "specialist-worker"
    )
    assert hooks["SubagentStop"][0]["matcher"] == (
        "specialist-worker"
    )


def test_hook_handlers_use_cross_platform_exec_form():
    hooks = read_settings()["hooks"]

    handlers = []
    for groups in hooks.values():
        for group in groups:
            handlers.extend(group["hooks"])

    for handler in handlers:
        assert handler["type"] == "command"
        assert handler["command"] == "python"
        assert handler["args"] == [
            (
                "${CLAUDE_PROJECT_DIR}/tools/"
                "claude_hooks/runtime_hooks.py"
            )
        ]
        assert handler["timeout"] == 5


def test_normal_development_session_is_ignored(tmp_path):
    payload = {
        "session_id": "dev-session",
        "cwd": str(ROOT),
        "permission_mode": "default",
        "hook_event_name": "UserPromptSubmit",
        "prompt": "development prompt",
    }

    result, output, audit_dir = run_hook(
        payload,
        tmp_path,
        provider="anthropic",
    )

    assert result.returncode == 0
    assert output is None
    assert not audit_dir.exists()


def test_runtime_preflight_passes_current_c14_contract(tmp_path):
    payload = runtime_payload("UserPromptSubmit")
    payload["prompt"] = "run server 1"

    result, output, audit_dir = run_hook(
        payload,
        tmp_path,
    )

    assert result.returncode == 0
    assert "decision" not in output
    assert "preflight passed" in (
        output["hookSpecificOutput"]["additionalContext"]
    )

    files = list(audit_dir.rglob("*.json"))
    assert files


def test_runtime_preflight_blocks_non_ollama_provider(tmp_path):
    payload = runtime_payload("UserPromptSubmit")

    result, output, _ = run_hook(
        payload,
        tmp_path,
        provider="anthropic",
    )

    assert result.returncode == 0
    assert output["decision"] == "block"
    assert "AI_VPS_LLM_PROVIDER" in output["reason"]


def test_session_start_adds_runtime_context_without_blocking(
    tmp_path,
):
    payload = runtime_payload("SessionStart")
    payload["source"] = "startup"
    payload["model"] = "runtime-model"

    result, output, _ = run_hook(payload, tmp_path)

    assert result.returncode == 0
    assert "decision" not in output
    assert (
        output["hookSpecificOutput"]["hookEventName"]
        == "SessionStart"
    )


def test_runtime_config_change_is_blocked(tmp_path):
    payload = runtime_payload("ConfigChange")
    payload["source"] = "project_settings"
    payload["file_path"] = str(
        ROOT / ".claude/settings.json"
    )

    _, output, _ = run_hook(payload, tmp_path)

    assert output["decision"] == "block"
    assert "immutable" in output["reason"]


def test_specialist_lifecycle_audit_does_not_store_prompt_or_output(
    tmp_path,
):
    payload = {
        "session_id": "session-test",
        "cwd": str(ROOT),
        "permission_mode": "dontAsk",
        "hook_event_name": "SubagentStart",
        "agent_type": "specialist-worker",
        "agent_id": "worker-1",
        "prompt": "SECRET_PROMPT_MUST_NOT_BE_STORED",
    }

    _, output, audit_dir = run_hook(payload, tmp_path)

    assert (
        output["hookSpecificOutput"]["hookEventName"]
        == "SubagentStart"
    )

    files = list(audit_dir.rglob("*.json"))
    assert len(files) == 1

    stored = files[0].read_text(encoding="utf-8")
    assert "SECRET_PROMPT_MUST_NOT_BE_STORED" not in stored
    assert "specialist-worker" in stored


def test_runtime_event_directory_is_gitignored():
    gitignore = (ROOT / ".gitignore").read_text(
        encoding="utf-8"
    )

    assert ".claude/runtime-events/" in gitignore
