import asyncio
import json

import httpx

from app.agent.investigation.specialist_reasoning_client import (
    OllamaSpecialistReasoningClient,
)


class FakeResponse:
    def __init__(
        self,
        *,
        status_code=200,
        payload=None,
        text="",
    ):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

        request = httpx.Request(
            "POST",
            "http://localhost:11434/api/chat",
        )

        self._response = httpx.Response(
            status_code=status_code,
            request=request,
            text=text,
        )

    def raise_for_status(self):
        self._response.raise_for_status()

    def json(self):
        return self._payload


class FakeHTTPClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    async def post(self, path, json):
        self.requests.append((path, json))
        return self.responses.pop(0)


def valid_content():
    return json.dumps(
        {
            "summary": "NGINX requires live status evidence.",
            "confidence": 0.3,
            "findings": [],
            "hypotheses": [],
            "ruled_out": [],
            "missing_evidence": [
                "Current NGINX service status."
            ],
            "recommended_next_specialists": [],
            "diagnostic_tool_requests": [
                {
                    "tool_id": "systemd-status",
                    "arguments": {
                        "service": "nginx",
                    },
                    "rationale": "Check NGINX service state.",
                }
            ],
        }
    )


def make_client(responses):
    client = OllamaSpecialistReasoningClient(
        base_url="http://localhost:11434",
        model="test-model",
        timeout_seconds=30,
    )
    fake = FakeHTTPClient(responses)
    client._client = fake
    return client, fake


def test_schema_http_400_falls_back_to_json_mode():
    client, fake = make_client(
        [
            FakeResponse(
                status_code=400,
                text="schema format unsupported",
            ),
            FakeResponse(
                payload={
                    "done": True,
                    "done_reason": "stop",
                    "message": {
                        "content": valid_content(),
                    },
                },
            ),
        ]
    )

    output = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(fake.requests) == 2
    assert isinstance(fake.requests[0][1]["format"], dict)
    assert fake.requests[1][1]["format"] == "json"
    assert (
        output.diagnostic_tool_requests[0].tool_id
        == "systemd-status"
    )


def test_bad_json_retries_once_in_json_mode():
    client, fake = make_client(
        [
            FakeResponse(
                payload={
                    "done": True,
                    "done_reason": "length",
                    "message": {
                        "content": '{"summary":"bad',
                    },
                },
            ),
            FakeResponse(
                payload={
                    "done": True,
                    "done_reason": "stop",
                    "message": {
                        "content": valid_content(),
                    },
                },
            ),
        ]
    )

    output = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(fake.requests) == 2
    assert isinstance(fake.requests[0][1]["format"], dict)
    assert fake.requests[1][1]["format"] == "json"
    assert fake.requests[0][1]["options"]["num_predict"] == 6144
    assert fake.requests[1][1]["options"]["num_predict"] == 8192
    assert output.summary


def test_valid_schema_output_needs_one_request():
    client, fake = make_client(
        [
            FakeResponse(
                payload={
                    "done": True,
                    "done_reason": "stop",
                    "message": {
                        "content": valid_content(),
                    },
                },
            ),
        ]
    )

    asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(fake.requests) == 1
    assert isinstance(fake.requests[0][1]["format"], dict)
