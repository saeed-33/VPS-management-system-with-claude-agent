#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import shutil
from pathlib import Path

HELPER = 'def _valid_project_mcp_command(server: dict[str, Any]) -> bool:\n    """\n    Accept only the project\'s bounded stdio MCP runner.\n\n    Supports both the original launch form and the C.14.7 hardened\n    uv invocation.\n    """\n    if server.get("command") != "uv":\n        return False\n\n    args = server.get("args")\n    if not isinstance(args, list):\n        return False\n\n    if not all(isinstance(item, str) for item in args):\n        return False\n\n    original = [\n        "run",\n        "python",\n        "tools/run_project_mcp_server.py",\n    ]\n\n    hardened = [\n        "run",\n        "--no-sync",\n        "--project",\n        "${CLAUDE_PROJECT_DIR:-.}",\n        "python",\n        (\n            "${CLAUDE_PROJECT_DIR:-.}/"\n            "tools/run_project_mcp_server.py"\n        ),\n    ]\n\n    return args in (original, hardened)\n'
TESTS_APPEND = '\n\n\ndef test_runtime_preflight_accepts_hardened_project_mcp_command(\n    tmp_path,\n):\n    payload = runtime_payload("UserPromptSubmit")\n    payload["prompt"] = "run server 2"\n\n    result, output, _ = run_hook(\n        payload,\n        tmp_path,\n    )\n\n    assert result.returncode == 0\n    assert output is not None\n    assert "decision" not in output\n    assert (\n        "preflight passed"\n        in output["hookSpecificOutput"]["additionalContext"]\n    )\n\n\ndef test_project_mcp_validation_accepts_hardened_argv():\n    hook_source = HOOK.read_text(encoding="utf-8")\n\n    assert "def _valid_project_mcp_command" in hook_source\n    assert \'"--no-sync"\' in hook_source\n    assert \'"--project"\' in hook_source\n    assert \'"${CLAUDE_PROJECT_DIR:-.}"\' in hook_source\n'


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fix C.14.7 runtime hook MCP preflight deadlock."
    )
    parser.add_argument("repo", nargs="?", default=".")
    return parser.parse_args()


def main() -> int:
    repo = Path(parse_args().repo).resolve()

    hook_path = repo / "tools" / "claude_hooks" / "runtime_hooks.py"
    test_path = repo / "tests" / "test_claude_runtime_hooks.py"

    for path in (hook_path, test_path):
        if not path.is_file():
            raise SystemExit(f"Required file missing: {path}")

    backup = repo / ".c14-7-hook-preflight-backup"
    if backup.exists():
        shutil.rmtree(backup)

    for source in (hook_path, test_path):
        rel = source.relative_to(repo)
        target = backup / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    source = hook_path.read_text(encoding="utf-8")

    if "def _valid_project_mcp_command(" not in source:
        marker = "\ndef _preflight_errors("
        if marker not in source:
            raise SystemExit(
                "Could not locate _preflight_errors insertion point."
            )

        source = source.replace(
            marker,
            "\n" + HELPER.rstrip() + "\n\n\ndef _preflight_errors(",
            1,
        )

    old_validation = (
        '            if server.get("command") != "uv":\n'
        '                errors.append("vps MCP command must be \'uv\'")\n'
        '            if server.get("args") != [\n'
        '                "run",\n'
        '                "python",\n'
        '                "tools/run_project_mcp_server.py",\n'
        '            ]:\n'
        '                errors.append(\n'
        '                    "vps MCP args do not match project MCP runner"\n'
        '                )\n'
    )

    new_validation = (
        '            if not _valid_project_mcp_command(server):\n'
        '                errors.append(\n'
        '                    "vps MCP command does not match an approved "\n'
        '                    "project MCP runner form"\n'
        '                )\n'
    )

    if old_validation in source:
        source = source.replace(
            old_validation,
            new_validation,
            1,
        )
    elif "if not _valid_project_mcp_command(server):" not in source:
        raise SystemExit(
            "Could not replace legacy exact MCP argv validation."
        )

    ast.parse(source, filename=str(hook_path))

    hook_path.write_text(
        source,
        encoding="utf-8",
        newline="\n",
    )

    tests = test_path.read_text(encoding="utf-8")

    if (
        "test_runtime_preflight_accepts_hardened_project_mcp_command"
        not in tests
    ):
        tests = tests.rstrip() + TESTS_APPEND + "\n"

    ast.parse(tests, filename=str(test_path))

    test_path.write_text(
        tests,
        encoding="utf-8",
        newline="\n",
    )

    final_source = hook_path.read_text(encoding="utf-8")

    for marker in (
        "def _valid_project_mcp_command(",
        '"--no-sync"',
        '"--project"',
        '"${CLAUDE_PROJECT_DIR:-.}"',
        "if not _valid_project_mcp_command(server):",
    ):
        if marker not in final_source:
            raise SystemExit(
                f"Verification failed: missing {marker}"
            )

    print("C.14.7 runtime hook MCP preflight deadlock fixed.")
    print(f"Backup: {backup}")
    print()
    print(
        "Run: uv run python -m pytest "
        "tests\\test_claude_runtime_hooks.py"
    )
    print(
        "Then: uv run python .\\diagnose_c14_7_tool_visibility.py"
    )
    print(
        "Expected: assistant_tool_use_names contains "
        "mcp__vps__get_server_context and DECISION=C."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
