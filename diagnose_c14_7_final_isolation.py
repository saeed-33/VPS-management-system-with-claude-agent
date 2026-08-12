from __future__ import annotations

import asyncio
import json
import os
import sys
import urllib.error
import urllib.request
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


TOOL = "mcp__vps__get_server_context"


def post_json(url: str, payload: dict) -> tuple[int, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = raw
        return exc.code, body


def direct_exact_name_probe(base_url: str, model: str) -> dict:
    payload = {
        "model": model,
        "max_tokens": 256,
        "stream": False,
        "tools": [
            {
                "name": TOOL,
                "description": "Read persisted context for one server.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "server_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["server_id"],
                    "additionalProperties": False,
                },
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Call {TOOL} for server_id 2 now. "
                    "Do not answer with prose. Use the tool."
                ),
            }
        ],
    }

    status, body = post_json(
        f"{base_url.rstrip('/')}/v1/messages",
        payload,
    )

    names: list[str] = []
    types: list[str] = []
    texts: list[str] = []
    stop_reason = None

    if isinstance(body, dict):
        stop_reason = body.get("stop_reason")
        content = body.get("content")
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                kind = block.get("type")
                if isinstance(kind, str):
                    types.append(kind)
                if kind == "tool_use":
                    name = block.get("name")
                    if isinstance(name, str):
                        names.append(name)
                if kind == "text":
                    text = block.get("text")
                    if isinstance(text, str) and text.strip():
                        texts.append(text.strip())

    return {
        "http_status": status,
        "tool_use_names": names,
        "content_block_types": types,
        "stop_reason": stop_reason,
        "text_preview": "\n".join(texts)[:1200] if texts else None,
    }


def parse_events(stdout: str) -> list[dict]:
    stripped = stdout.strip()
    if not stripped:
        return []

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        payload = None

    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
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


def summarize_events(events: list[dict]) -> dict:
    init = next(
        (
            e for e in events
            if e.get("type") == "system"
            and e.get("subtype") == "init"
        ),
        None,
    )

    result = next(
        (
            e for e in reversed(events)
            if e.get("type") == "result"
        ),
        None,
    )

    calls: list[str] = []
    texts: list[str] = []

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

            if block.get("type") == "tool_use":
                name = block.get("name")
                if isinstance(name, str):
                    calls.append(name)

            if block.get("type") == "text":
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    texts.append(text.strip())

    tools: list[str] = []
    mcp_servers = None

    if isinstance(init, dict):
        raw_tools = init.get("tools")
        if isinstance(raw_tools, list):
            tools = [
                item
                for item in raw_tools
                if isinstance(item, str)
            ]
        mcp_servers = init.get("mcp_servers")

    result_summary = None
    if isinstance(result, dict):
        result_summary = {
            "subtype": result.get("subtype"),
            "is_error": result.get("is_error"),
            "num_turns": result.get("num_turns"),
            "stop_reason": result.get("stop_reason"),
            "session_id": result.get("session_id"),
        }

    return {
        "mcp_servers": mcp_servers,
        "tool_visible": TOOL in tools,
        "assistant_tool_use_names": calls,
        "assistant_text_preview": "\n---\n".join(texts)[:2000]
        if texts
        else None,
        "result": result_summary,
    }


async def run_claude_probe(*, with_agent: bool) -> dict:
    model = settings.effective_claude_runtime_model

    builder = OllamaClaudeCommandBuilder(
        project_root=ROOT,
        model=model,
        base_url=settings.ollama_base_url,
        executable=settings.claude_runtime_executable,
        agent=settings.claude_runtime_agent,
    )

    request = ClaudeRuntimeRequest(
        job_id=(
            "c14-7-agent-probe"
            if with_agent
            else "c14-7-no-agent-probe"
        ),
        job_type="diagnostic",
        prompt=(
            f"Call {TOOL} for server_id 2 exactly once. "
            "Do not explain, simulate, or answer from memory. "
            "The next action must be the tool call. "
            "After the tool result, reply DONE."
        ),
        context={},
        timeout_seconds=120,
        max_turns=3,
        allowed_tools=(TOOL,),
        metadata={"diagnostic": True},
    )

    command = builder.build(request)
    argv = list(command.argv)
    env = {**os.environ, **command.env}

    if not with_agent:
        try:
            index = argv.index("--agent")
        except ValueError:
            pass
        else:
            del argv[index:index + 2]

        # Ensure project hooks do not classify this raw control run as the
        # operational server-supervisor session.
        env.pop("AI_VPS_CLAUDE_RUNTIME", None)
        env.pop("AI_VPS_CLAUDE_RUNTIME_AGENT", None)

    process = await asyncio.create_subprocess_exec(
        *argv,
        cwd=str(command.cwd or ROOT),
        env=env,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_bytes, stderr_bytes = await asyncio.wait_for(
        process.communicate(),
        timeout=120,
    )

    stdout = stdout_bytes.decode("utf-8", errors="replace")
    stderr = stderr_bytes.decode("utf-8", errors="replace")

    events = parse_events(stdout)
    summary = summarize_events(events)
    summary["returncode"] = process.returncode
    summary["event_count"] = len(events)
    summary["stderr_preview"] = (
        stderr.strip()[:1500] if stderr.strip() else None
    )
    return summary


async def main() -> int:
    model = settings.effective_claude_runtime_model
    base_url = settings.ollama_base_url

    print("C.14.7 final isolation diagnostic")
    print(f"root={ROOT}")
    print(f"model={model}")
    print(f"tool={TOOL}")

    print()
    print("=== Probe 1: direct Anthropic API, exact MCP-style tool name ===")
    direct = direct_exact_name_probe(base_url, model)
    print(json.dumps(direct, ensure_ascii=False, indent=2))

    print()
    print("=== Probe 2: Claude Code + MCP, WITHOUT --agent/runtime hooks ===")
    raw = await run_claude_probe(with_agent=False)
    print(json.dumps(raw, ensure_ascii=False, indent=2))

    print()
    print("=== Probe 3: Claude Code + MCP + server-supervisor ===")
    agent = await run_claude_probe(with_agent=True)
    print(json.dumps(agent, ensure_ascii=False, indent=2))

    direct_ok = TOOL in direct.get("tool_use_names", [])
    raw_ok = TOOL in raw.get("assistant_tool_use_names", [])
    agent_ok = TOOL in agent.get("assistant_tool_use_names", [])

    print()
    print("=== DECISION ===")

    if not direct_ok:
        print(
            "D1: The model/API does not emit the exact MCP-style tool name. "
            "This is a model/tool-name compatibility issue."
        )
    elif direct_ok and not raw_ok:
        print(
            "D2: Direct Ollama emits the exact tool call, but raw Claude Code "
            "does not. The fault is Claude Code request shaping/compatibility, "
            "not the project agent."
        )
    elif direct_ok and raw_ok and not agent_ok:
        print(
            "D3: Raw Claude Code tool calling works, but server-supervisor "
            "suppresses it. The fault is the agent/system-prompt contract."
        )
    else:
        print(
            "D4: Direct Ollama, raw Claude Code, and server-supervisor all "
            "call the tool. The transport is healthy; investigate only the "
            "full monitoring workflow prompt."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
