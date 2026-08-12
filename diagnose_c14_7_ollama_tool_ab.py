from __future__ import annotations

import json
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

from app.shared.config import settings


def request_json(url: str, payload: dict | None = None) -> tuple[int, dict | list | str]:
    data = None
    headers = {"Content-Type": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            raw = response.read().decode("utf-8", errors="replace")
            try:
                decoded = json.loads(raw)
            except json.JSONDecodeError:
                decoded = raw
            return response.status, decoded
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError:
            decoded = raw
        return exc.code, decoded


def anthropic_probe(base_url: str, model: str) -> dict:
    payload = {
        "model": model,
        "max_tokens": 256,
        "stream": False,
        "tools": [
            {
                "name": "get_server_context",
                "description": (
                    "Read the persisted context for exactly one registered server."
                ),
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
                    "Call get_server_context for server_id 2 now. "
                    "Do not answer with prose. Use the tool."
                ),
            }
        ],
    }

    status, body = request_json(
        f"{base_url.rstrip('/')}/v1/messages",
        payload,
    )

    result = {
        "http_status": status,
        "tool_use_names": [],
        "content_block_types": [],
        "stop_reason": None,
        "text_preview": None,
    }

    if isinstance(body, dict):
        result["stop_reason"] = body.get("stop_reason")
        content = body.get("content")

        if isinstance(content, list):
            texts = []
            for block in content:
                if not isinstance(block, dict):
                    continue

                block_type = block.get("type")
                if isinstance(block_type, str):
                    result["content_block_types"].append(block_type)

                if block_type == "tool_use":
                    name = block.get("name")
                    if isinstance(name, str):
                        result["tool_use_names"].append(name)

                if block_type == "text":
                    text = block.get("text")
                    if isinstance(text, str) and text.strip():
                        texts.append(text.strip())

            if texts:
                result["text_preview"] = "\n".join(texts)[:1000]
    else:
        result["body_preview"] = repr(body)[:1000]

    return result


def native_probe(base_url: str, model: str) -> dict:
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Call get_server_context for server_id 2 now. "
                    "Do not answer with prose. Use the tool."
                ),
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_server_context",
                    "description": (
                        "Read the persisted context for exactly one registered server."
                    ),
                    "parameters": {
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
                },
            }
        ],
    }

    status, body = request_json(
        f"{base_url.rstrip('/')}/api/chat",
        payload,
    )

    result = {
        "http_status": status,
        "tool_call_names": [],
        "done_reason": None,
        "text_preview": None,
    }

    if isinstance(body, dict):
        result["done_reason"] = body.get("done_reason")
        message = body.get("message")

        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                result["text_preview"] = content.strip()[:1000]

            tool_calls = message.get("tool_calls")
            if isinstance(tool_calls, list):
                for call in tool_calls:
                    if not isinstance(call, dict):
                        continue
                    function = call.get("function")
                    if not isinstance(function, dict):
                        continue
                    name = function.get("name")
                    if isinstance(name, str):
                        result["tool_call_names"].append(name)
    else:
        result["body_preview"] = repr(body)[:1000]

    return result


def main() -> int:
    base_url = settings.ollama_base_url.rstrip("/")
    model = settings.effective_claude_runtime_model

    print("C.14.7 Ollama tool-call A/B diagnostic")
    print(f"base_url={base_url}")
    print(f"model={model}")

    version_status, version_body = request_json(
        f"{base_url}/api/version"
    )
    print()
    print("=== Ollama version ===")
    print(f"http_status={version_status}")
    print(
        "body="
        + json.dumps(
            version_body,
            ensure_ascii=False,
        )[:1000]
    )

    print()
    print("=== Probe A: Anthropic compatibility /v1/messages ===")
    anthropic = anthropic_probe(base_url, model)
    print(
        json.dumps(
            anthropic,
            ensure_ascii=False,
            indent=2,
        )
    )

    print()
    print("=== Probe B: Native Ollama /api/chat ===")
    native = native_probe(base_url, model)
    print(
        json.dumps(
            native,
            ensure_ascii=False,
            indent=2,
        )
    )

    anthropic_ok = (
        "get_server_context"
        in anthropic.get("tool_use_names", [])
        and anthropic.get("stop_reason") == "tool_use"
    )
    native_ok = (
        "get_server_context"
        in native.get("tool_call_names", [])
    )

    print()
    print("=== DECISION ===")

    if anthropic_ok and native_ok:
        print(
            "C: Both Ollama APIs produce a real tool call. "
            "The remaining fault is inside Claude Code/request shaping."
        )
    elif native_ok and not anthropic_ok:
        print(
            "A: Native Ollama tool calling works, but Anthropic "
            "compatibility does not produce tool_use. "
            "The fault is the Ollama Anthropic compatibility path."
        )
    elif anthropic_ok and not native_ok:
        print(
            "D: Anthropic compatibility produced tool_use while the native "
            "probe did not. Re-run once; this is an unexpected model/API split."
        )
    else:
        print(
            "B: Neither API produced a real tool call. "
            "The model/service response is the blocking layer; "
            "do not modify Claude runtime code."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
