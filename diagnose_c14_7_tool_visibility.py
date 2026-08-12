from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
if (SCRIPT.parent / "app").is_dir():
    ROOT = SCRIPT.parent
elif (SCRIPT.parent.parent / "app").is_dir():
    ROOT = SCRIPT.parent.parent
else:
    raise SystemExit("Could not locate project root.")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.runtime.claude.models import ClaudeRuntimeRequest
from app.runtime.claude.ollama_runtime import OllamaClaudeCommandBuilder
from app.shared.config import settings


def parse_events(stdout: str) -> list[dict]:
    stripped = stdout.strip()
    if not stripped:
        return []

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        payload = None

    if isinstance(payload, list):
        return [
            x for x in payload
            if isinstance(x, dict)
        ]

    if isinstance(payload, dict):
        return [payload]

    events: list[dict] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)

    return events


def tool_use_names(events: list[dict]) -> list[str]:
    result: list[str] = []

    for event in events:
        if event.get("type") != "assistant":
            continue

        message = event.get("message")
        if not isinstance(message, dict):
            continue

        content = message.get("content")
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue

            name = block.get("name")
            if isinstance(name, str):
                result.append(name)

    return result


async def main() -> int:
    model = settings.effective_claude_runtime_model
    executable = settings.claude_runtime_executable

    print("C.14.7 exact runtime tool visibility diagnostic")
    print(f"root={ROOT}")
    print(f"model={model}")
    print(f"agent={settings.claude_runtime_agent}")

    builder = OllamaClaudeCommandBuilder(
        project_root=ROOT,
        model=model,
        base_url=settings.ollama_base_url,
        executable=executable,
        agent=settings.claude_runtime_agent,
    )

    request = ClaudeRuntimeRequest(
        job_id="c14-7-tool-visibility",
        job_type="diagnostic",
        prompt=(
            "Diagnostic execution. "
            "For server_id=2, call "
            "mcp__vps__get_server_context exactly once. "
            "Do not simulate or describe the call. "
            "Do not use any other tool. "
            "After the tool returns, reply with the word DONE."
        ),
        context={},
        timeout_seconds=120,
        max_turns=3,
        allowed_tools=(
            "mcp__vps__get_server_context",
        ),
        metadata={"diagnostic": True},
    )

    command = builder.build(request)

    process = await asyncio.create_subprocess_exec(
        *command.argv,
        cwd=str(command.cwd or ROOT),
        env={**os.environ, **command.env},
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_bytes, stderr_bytes = await asyncio.wait_for(
        process.communicate(),
        timeout=120,
    )

    stdout = stdout_bytes.decode(
        "utf-8",
        errors="replace",
    )
    stderr = stderr_bytes.decode(
        "utf-8",
        errors="replace",
    )

    events = parse_events(stdout)

    print(f"returncode={process.returncode}")
    print(f"event_count={len(events)}")

    init = next(
        (
            event
            for event in events
            if (
                event.get("type") == "system"
                and event.get("subtype") == "init"
            )
        ),
        None,
    )

    if init is None:
        print("INIT_EVENT=MISSING")
    else:
        print("INIT_EVENT=FOUND")

        mcp_servers = init.get("mcp_servers")
        print(
            "mcp_servers="
            + json.dumps(
                mcp_servers,
                ensure_ascii=False,
            )
        )

        tools = init.get("tools")
        if not isinstance(tools, list):
            tools = []

        vps_tools = [
            tool
            for tool in tools
            if (
                isinstance(tool, str)
                and (
                    tool.startswith("mcp__vps__")
                    or tool in {
                        "ToolSearch",
                        "WaitForMcpServers",
                    }
                )
            )
        ]

        print(f"init_tool_count={len(tools)}")
        print(
            "relevant_init_tools="
            + json.dumps(
                vps_tools,
                ensure_ascii=False,
            )
        )

    calls = tool_use_names(events)
    print(
        "assistant_tool_use_names="
        + json.dumps(
            calls,
            ensure_ascii=False,
        )
    )

    result = next(
        (
            event
            for event in reversed(events)
            if event.get("type") == "result"
        ),
        None,
    )

    if result is None:
        print("RESULT_EVENT=MISSING")
    else:
        print(
            "result="
            + json.dumps(
                {
                    "subtype": result.get("subtype"),
                    "is_error": result.get("is_error"),
                    "num_turns": result.get("num_turns"),
                    "stop_reason": result.get("stop_reason"),
                    "session_id": result.get("session_id"),
                },
                ensure_ascii=False,
            )
        )

    if stderr.strip():
        print(
            "stderr_preview="
            + repr(stderr.strip()[:2000])
        )

    print()
    print("DECISION:")
    if init is None:
        print("A: Claude did not emit system/init.")
    else:
        tools = init.get("tools")
        tools = tools if isinstance(tools, list) else []
        visible_vps = [
            x
            for x in tools
            if (
                isinstance(x, str)
                and x.startswith("mcp__vps__")
            )
        ]

        if visible_vps:
            if any(
                x == "mcp__vps__get_server_context"
                for x in calls
            ):
                print(
                    "C: VPS MCP tool is visible AND model called it. "
                    "Runtime/tool transport is healthy."
                )
            else:
                print(
                    "B2: VPS MCP tools are visible but the model did not "
                    "call even the explicitly requested tool."
                )
        else:
            print(
                "B1: VPS MCP tools are NOT present in system/init.tools. "
                "Fix Claude tool availability/config; do not change model."
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
