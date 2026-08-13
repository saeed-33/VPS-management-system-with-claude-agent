import asyncio
import json

import httpx

from app.capabilities.investigation.specialist_reasoning_client import (
    OllamaSpecialistReasoningClient,
)


VALID_OUTPUT = {
    "summary": "Concise result.",
    "confidence": 0.7,
    "findings": [],
    "hypotheses": [],
    "ruled_out": [],
    "missing_evidence": [],
    "recommended_next_specialists": [],
    "diagnostic_tool_requests": [],
}

FINAL_SYNTHESIS_OUTPUT = {
    "summary": "Concise result.",
    "confidence": 0.7,
    "missing_evidence": [],
    "recommended_next_specialists": [],
}


def make_response(status_code, payload, request):
    return httpx.Response(
        status_code,
        json=payload,
        request=request,
    )


def test_schema_rejection_is_cached_and_json_fallback_succeeds():
    calls = []
    schema_rejected = False

    async def handler(request):
        nonlocal schema_rejected

        body = json.loads(request.content)
        calls.append(body)

        if (
            not schema_rejected
            and body["format"] != "json"
        ):
            schema_rejected = True
            return make_response(
                400,
                {"error": "failed to parse grammar"},
                request,
            )

        return make_response(
            200,
            {
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(VALID_OUTPUT)
                },
            },
            request,
        )

    client = OllamaSpecialistReasoningClient(
        base_url="http://ollama.test",
        model="test-model",
        timeout_seconds=10,
    )
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="http://ollama.test",
    )

    parsed = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert parsed.summary == "Concise result."
    assert calls[0]["format"] != "json"
    assert calls[1]["format"] == "json"
    assert client._schema_format_supported is False

    calls.clear()

    asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(calls) == 1
    assert calls[0]["format"] == "json"

    asyncio.run(client.close())


def test_length_retry_uses_compact_retry_instruction():
    calls = []

    async def handler(request):
        body = json.loads(request.content)
        calls.append(body)

        if len(calls) == 1:
            return make_response(
                200,
                {
                    "done_reason": "length",
                    "message": {
                        "content": '{"summary":"truncated"'
                    },
                },
                request,
            )

        return make_response(
            200,
            {
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(VALID_OUTPUT)
                },
            },
            request,
        )

    client = OllamaSpecialistReasoningClient(
        base_url="http://ollama.test",
        model="test-model",
        timeout_seconds=10,
    )
    client._schema_format_supported = False
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="http://ollama.test",
    )

    parsed = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert parsed.summary == "Concise result."
    assert len(calls) == 2

    first_prompt = calls[0]["messages"][1]["content"]
    second_prompt = calls[1]["messages"][1]["content"]

    assert "## Structured Output Contract" in first_prompt
    assert "## Retry Requirement" not in first_prompt
    assert "## Retry Requirement" in second_prompt
    assert "Prefer fewer findings" in second_prompt

    asyncio.run(client.close())

def test_final_synthesis_enables_provider_compact_mode():
    calls = []

    async def handler(request):
        body = json.loads(request.content)
        calls.append(body)

        return make_response(
            200,
            {
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(FINAL_SYNTHESIS_OUTPUT)
                },
            },
            request,
        )

    client = OllamaSpecialistReasoningClient(
        base_url="http://ollama.test",
        model="test-model",
        timeout_seconds=10,
    )
    client._schema_format_supported = False
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="http://ollama.test",
    )

    asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt=(
                "context\n\n"
                "## Final Synthesis Required\n"
                "No more Tools."
            ),
        )
    )

    prompt = calls[0]["messages"][1]["content"]

    assert "Provider Final-Synthesis Compact Mode" in prompt
    assert "Allowed keys are only: summary, confidence" in prompt
    assert "Do not output findings, hypotheses, ruled_out" in prompt
    assert calls[0]["options"]["num_predict"] == 6144
    assert calls[0]["options"]["num_ctx"] == 32768

    asyncio.run(client.close())

