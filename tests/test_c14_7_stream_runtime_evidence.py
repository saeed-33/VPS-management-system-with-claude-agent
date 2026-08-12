import json

import pytest

from app.runtime.claude.exceptions import (
    ClaudeProcessOutputError,
)
from app.runtime.claude.session_runner import (
    ClaudeCliJsonDecoder,
)


def _required_events():
    return [
        {
            "type": "system",
            "subtype": "init",
            "session_id": "s-1",
            "mcp_servers": [
                {
                    "name": "vps",
                    "status": "connected",
                }
            ],
        },
        {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "mcp__vps__run_monitoring",
                        "input": {
                            "server_id": 2,
                        },
                    },
                    {
                        "type": "tool_use",
                        "name": "mcp__vps__analyze_report",
                        "input": {
                            "report_id": 1,
                        },
                    },
                ]
            },
        },
        {
            "type": "result",
            "subtype": "success",
            "session_id": "s-1",
            "num_turns": 3,
            "is_error": False,
            "usage": {},
        },
    ]


def test_stream_json_operational_success_is_evidence_based():
    decoder = ClaudeCliJsonDecoder()

    stdout = "\n".join(
        json.dumps(event)
        for event in _required_events()
    )

    result = decoder.decode(
        stdout
    )

    payload = json.loads(
        result.content
    )

    assert payload["status"] == "completed"
    assert (
        payload["metadata"]["result_source"]
        == "runtime_mcp_evidence"
    )
    assert result.tool_call_count == 2
    assert result.usage_metadata[
        "event_mcp_servers"
    ][0]["status"] == "connected"


def test_operational_success_rejects_failed_mcp():
    events = _required_events()
    events[0]["mcp_servers"][0][
        "status"
    ] = "failed"

    decoder = ClaudeCliJsonDecoder()

    with pytest.raises(
        ClaudeProcessOutputError,
        match="vps MCP status",
    ):
        decoder.decode(
            json.dumps(events)
        )


def test_operational_success_rejects_missing_required_tool():
    events = _required_events()
    events[1]["message"]["content"] = (
        events[1]["message"]["content"][:1]
    )

    decoder = ClaudeCliJsonDecoder()

    with pytest.raises(
        ClaudeProcessOutputError,
        match="required project MCP tools were not called",
    ):
        decoder.decode(
            json.dumps(events)
        )


def test_result_error_subtype_is_not_accepted():
    events = _required_events()
    events[-1]["subtype"] = (
        "error_max_turns"
    )
    events[-1]["is_error"] = True

    decoder = ClaudeCliJsonDecoder()

    with pytest.raises(
        ClaudeProcessOutputError,
        match="error_max_turns",
    ):
        decoder.decode(
            json.dumps(events)
        )
