import asyncio
import json

from app.domain.investigation.specialist_reasoning_client import (
    OllamaSpecialistReasoningClient,
)


class Response:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class HTTPClient:
    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.requests = []

    async def post(self, path, json):
        self.requests.append((path, json))
        return Response(self.payloads.pop(0))


def valid_content():
    return json.dumps(
        {
            "summary": "NGINX state requires live evidence.",
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
                        "service": "nginx"
                    },
                    "rationale": "Check current service state."
                }
            ],
        }
    )


def make_client(payloads):
    client = OllamaSpecialistReasoningClient(
        base_url="http://localhost:11434",
        model="test-model",
        timeout_seconds=30,
    )
    fake = HTTPClient(payloads)
    client._client = fake
    return client, fake


def test_ollama_uses_json_schema_as_format():
    client, fake = make_client(
        [
            {
                "done": True,
                "done_reason": "stop",
                "message": {
                    "content": valid_content()
                },
            }
        ]
    )

    output = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    payload = fake.requests[0][1]

    assert isinstance(payload["format"], dict)
    assert payload["format"]["type"] == "object"
    assert output.confidence == 0.3


def test_ollama_retries_once_after_invalid_json():
    client, fake = make_client(
        [
            {
                "done": True,
                "done_reason": "length",
                "message": {
                    "content": "{\"summary\":\"unterminated"
                },
            },
            {
                "done": True,
                "done_reason": "stop",
                "message": {
                    "content": valid_content()
                },
            },
        ]
    )

    output = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(fake.requests) == 2
    assert fake.requests[0][1]["options"]["num_predict"] == 6144
    assert fake.requests[1][1]["options"]["num_predict"] == 8192
    assert output.summary


def test_ollama_valid_output_does_not_retry():
    client, fake = make_client(
        [
            {
                "done": True,
                "done_reason": "stop",
                "message": {
                    "content": valid_content()
                },
            }
        ]
    )

    asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(fake.requests) == 1
