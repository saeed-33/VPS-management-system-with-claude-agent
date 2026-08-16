"""
Hook يربط lifecycle الخاص بـClaude Runtime بسجلات أو سياسات المشروع.

الموقع في المعمارية: Claude runtime tooling.
يُستدعى بواسطة: Claude Code hooks.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يستبدل MCP أو application policy.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUNTIME_MAIN_AGENT = "server-supervisor"
RUNTIME_WORKER_AGENT = "specialist-worker"

SUPERVISED_REMEDIATION_TOOLS = {
    "mcp__vps__create_remediation_plan",
    "mcp__vps__test_remediation_in_sandbox",
    "mcp__vps__request_user_approval",
    "mcp__vps__apply_approved_remediation",
}

FORBIDDEN_REMEDIATION_TOOLS = {
    "mcp__vps__raw_ssh",
    "mcp__vps__raw_shell",
    "mcp__vps__execute_command",
}

REQUIRED_FILES = (
    ".mcp.json",
    ".claude/settings.json",
    ".claude/agents/server-supervisor.md",
    ".claude/agents/specialist-worker.md",
    ".claude/skills/monitor-server/SKILL.md",
    ".claude/skills/analyze-incident/SKILL.md",
    ".claude/skills/investigate-incident/SKILL.md",
    ".claude/skills/plan-remediation/SKILL.md",
)


def _read_input() -> dict[str, Any]:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _read_input؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد dict[str, Any] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    raw = sys.stdin.read()
    if not raw.strip():
        return {}

    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("Hook input must be a JSON object.")
    return value


def _project_root(payload: dict[str, Any]) -> Path:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _project_root؛ المدخلات المهمة: payload.
    تعيد Path أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    configured = os.environ.get("CLAUDE_PROJECT_DIR")
    if configured:
        return Path(configured).resolve()

    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        return Path(cwd).resolve()

    return Path.cwd().resolve()


def _safe_slug(value: object, fallback: str) -> str:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _safe_slug؛ المدخلات المهمة: value، fallback.
    تعيد str أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    text = str(value or fallback)
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-._")
    return (text or fallback)[:120]


def _audit_dir(root: Path) -> Path:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _audit_dir؛ المدخلات المهمة: root.
    تعيد Path أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    override = os.environ.get("AI_VPS_RUNTIME_HOOK_AUDIT_DIR")
    if override:
        return Path(override).resolve()
    return root / ".claude" / "runtime-events"


def _audit(payload: dict[str, Any], event: str) -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _audit؛ المدخلات المهمة: payload، event.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    root = _project_root(payload)
    target_root = _audit_dir(root)

    session_id = _safe_slug(
        payload.get("session_id"),
        "unknown-session",
    )
    agent_id = _safe_slug(
        payload.get("agent_id"),
        "main",
    )
    event_slug = _safe_slug(event, "unknown-event")

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hook_event_name": event,
        "session_id": payload.get("session_id"),
        "agent_type": payload.get("agent_type"),
        "agent_id": payload.get("agent_id"),
        "source": payload.get("source"),
        "model": payload.get("model"),
        "permission_mode": payload.get("permission_mode"),
        "stop_hook_active": payload.get("stop_hook_active"),
    }

    try:
        session_dir = target_root / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        filename = (
            f"{time.time_ns()}-{event_slug}-{agent_id}.json"
        )
        (session_dir / filename).write_text(
            json.dumps(
                record,
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError:
        # Hook audit is transitional local observability, not the
        # authoritative project audit store. Never crash the workflow
        # solely because this local trace could not be written.
        pass


def _is_main_runtime(payload: dict[str, Any]) -> bool:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _is_main_runtime؛ المدخلات المهمة: payload.
    تعيد bool أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if payload.get("agent_type") == RUNTIME_MAIN_AGENT:
        return True

    return (
        os.environ.get("AI_VPS_CLAUDE_RUNTIME") == "1"
        and os.environ.get(
            "AI_VPS_CLAUDE_RUNTIME_AGENT"
        )
        == RUNTIME_MAIN_AGENT
    )


def _is_worker(payload: dict[str, Any]) -> bool:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _is_worker؛ المدخلات المهمة: payload.
    تعيد bool أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return payload.get("agent_type") == RUNTIME_WORKER_AGENT


def _load_json(path: Path) -> dict[str, Any]:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _load_json؛ المدخلات المهمة: path.
    تعيد dict[str, Any] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _valid_project_mcp_command(server: dict[str, Any]) -> bool:
    """
    Accept only the project's bounded stdio MCP runner.

    Supports both the original launch form and the C.14.7 hardened
    uv invocation.
    """
    if server.get("command") != "uv":
        return False

    args = server.get("args")
    if not isinstance(args, list):
        return False

    if not all(isinstance(item, str) for item in args):
        return False

    original = [
        "run",
        "python",
        "tools/run_project_mcp_server.py",
    ]

    hardened = [
        "run",
        "--no-sync",
        "--project",
        "${CLAUDE_PROJECT_DIR:-.}",
        "python",
        (
            "${CLAUDE_PROJECT_DIR:-.}/"
            "tools/run_project_mcp_server.py"
        ),
    ]

    return args in (original, hardened)


def _preflight_errors(payload: dict[str, Any]) -> list[str]:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _preflight_errors؛ المدخلات المهمة: payload.
    تعيد list[str] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    root = _project_root(payload)
    errors: list[str] = []

    provider = os.environ.get(
        "AI_VPS_LLM_PROVIDER",
        "",
    ).strip().lower()
    if provider != "ollama":
        errors.append(
            "AI_VPS_LLM_PROVIDER must be 'ollama'"
        )

    cwd_raw = payload.get("cwd")
    if not isinstance(cwd_raw, str) or not cwd_raw.strip():
        errors.append("Claude hook input is missing cwd")
    else:
        cwd = Path(cwd_raw).resolve()
        if cwd != root:
            errors.append(
                "server-supervisor must start at CLAUDE_PROJECT_DIR"
            )

    permission_mode = payload.get("permission_mode")
    if permission_mode != "dontAsk":
        errors.append(
            "server-supervisor permission_mode must be 'dontAsk'"
        )

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing runtime file: {relative}")

    mcp_path = root / ".mcp.json"
    settings_path = root / ".claude" / "settings.json"

    if mcp_path.is_file():
        try:
            mcp = _load_json(mcp_path)
            server = (
                mcp.get("mcpServers", {})
                .get("vps", {})
            )
            if not _valid_project_mcp_command(server):
                errors.append(
                    "vps MCP command does not match an approved "
                    "project MCP runner form"
                )
        except (OSError, ValueError, json.JSONDecodeError):
            errors.append(".mcp.json is invalid")

    if settings_path.is_file():
        try:
            settings = _load_json(settings_path)
            permissions = settings.get("permissions", {})
            allow = set(permissions.get("allow", []))
            deny = set(permissions.get("deny", []))

            if "Agent(specialist-worker)" not in allow:
                errors.append(
                    "specialist-worker delegation is not pre-approved"
                )

            missing_denies = FORBIDDEN_REMEDIATION_TOOLS - deny
            if missing_denies:
                errors.append(
                    "raw remediation escape tools are not fully denied"
                )

            leaked_allows = FORBIDDEN_REMEDIATION_TOOLS & allow
            if leaked_allows:
                errors.append(
                    "raw remediation escape tools appear in allow list"
                )

            missing_supervised = SUPERVISED_REMEDIATION_TOOLS - allow
            if missing_supervised:
                errors.append("supervised remediation tools are not allowed")
            denied_supervised = SUPERVISED_REMEDIATION_TOOLS & deny
            if denied_supervised:
                errors.append("supervised remediation tools are denied")

            if settings.get(
                "disableSkillShellExecution"
            ) is not True:
                errors.append(
                    "Skill shell execution must remain disabled"
                )
        except (OSError, ValueError, json.JSONDecodeError):
            errors.append(".claude/settings.json is invalid")

    for relative in (
        ".claude/agents/server-supervisor.md",
        ".claude/agents/specialist-worker.md",
    ):
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "model: inherit" not in text:
            errors.append(f"{relative} must use model: inherit")
        if "permissionMode: dontAsk" not in text:
            errors.append(
                f"{relative} must use permissionMode: dontAsk"
            )

    return errors


def _session_start(payload: dict[str, Any]) -> dict[str, Any] | None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _session_start؛ المدخلات المهمة: payload.
    تعيد dict[str, Any] | None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if not _is_main_runtime(payload):
        return None

    _audit(payload, "SessionStart")

    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                "AI VPS runtime session detected. "
                "The project runtime contract requires Ollama, "
                "project MCP capabilities, DB-defined Specialists, "
                "evidence-grounded findings, and supervised remediation "
                "with persisted human approval. A blocking preflight runs "
                "before the user/runtime prompt is processed."
            ),
        }
    }


def _user_prompt_submit(
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _user_prompt_submit؛ المدخلات المهمة: payload.
    تعيد dict[str, Any] | None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if not _is_main_runtime(payload):
        return None

    errors = _preflight_errors(payload)

    _audit(
        payload,
        (
            "RuntimePreflightFailed"
            if errors
            else "RuntimePreflightPassed"
        ),
    )

    if errors:
        return {
            "decision": "block",
            "reason": (
                "AI VPS runtime preflight failed: "
                + "; ".join(errors)
            ),
        }

    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                "AI VPS runtime preflight passed. "
                "Remain inside the server-supervisor contract. "
                "Production writes require an unexpired persisted human "
                "approval whose plan fingerprint still matches."
            ),
        }
    }


def _config_change(payload: dict[str, Any]) -> dict[str, Any] | None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _config_change؛ المدخلات المهمة: payload.
    تعيد dict[str, Any] | None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if not _is_main_runtime(payload):
        return None

    _audit(payload, "ConfigChangeBlocked")

    return {
        "decision": "block",
        "reason": (
            "Runtime configuration and Skills are immutable "
            "during a server-supervisor session."
        ),
    }


def _subagent_start(payload: dict[str, Any]) -> dict[str, Any] | None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _subagent_start؛ المدخلات المهمة: payload.
    تعيد dict[str, Any] | None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if not _is_worker(payload):
        return None

    _audit(payload, "SubagentStart")

    return {
        "hookSpecificOutput": {
            "hookEventName": "SubagentStart",
            "additionalContext": (
                "Lifecycle guard: execute exactly one DB-defined "
                "Specialist task, do not delegate further, and "
                "return only project-owned result/Evidence IDs."
            ),
        }
    }


def _subagent_stop(payload: dict[str, Any]) -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _subagent_stop؛ المدخلات المهمة: payload.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if _is_worker(payload):
        _audit(payload, "SubagentStop")
    return None


def _session_end(payload: dict[str, Any]) -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى _session_end؛ المدخلات المهمة: payload.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if _is_main_runtime(payload):
        _audit(payload, "SessionEnd")
    return None


def dispatch(payload: dict[str, Any]) -> dict[str, Any] | None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى dispatch؛ المدخلات المهمة: payload.
    تعيد dict[str, Any] | None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    event = payload.get("hook_event_name")

    if event == "SessionStart":
        return _session_start(payload)
    if event == "UserPromptSubmit":
        return _user_prompt_submit(payload)
    if event == "ConfigChange":
        return _config_change(payload)
    if event == "SubagentStart":
        return _subagent_start(payload)
    if event == "SubagentStop":
        return _subagent_stop(payload)
    if event == "SessionEnd":
        return _session_end(payload)

    return None


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Claude runtime tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    try:
        payload = _read_input()
        output = dispatch(payload)
    except (ValueError, json.JSONDecodeError) as exc:
        # Malformed hook input is a configuration/runtime fault. For
        # blocking-capable events, returning a generic block is safer
        # than attempting to interpret partial untrusted input.
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        "AI VPS runtime hook input was invalid: "
                        f"{exc}"
                    ),
                }
            )
        )
        return 0

    if output is not None:
        print(
            json.dumps(
                output,
                ensure_ascii=False,
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
