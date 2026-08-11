import asyncio
import json

import httpx

from app.domain.investigation.specialist_reasoning_client import (
    OllamaSpecialistReasoningClient,
)


def test_final_synthesis_uses_minimal_json_mode():
    calls = []

    async def handler(request):
        body = json.loads(request.content)
        calls.append(body)

        return httpx.Response(
            200,
            json={
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(
                        {
                            "summary": "NGINX is not confirmed running.",
                            "confidence": 0.7,
                            "missing_evidence": [
                                "Direct process evidence."
                            ],
                            "recommended_next_specialists": [],
                        }
                    )
                },
            },
            request=request,
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

    output = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt=(
                "context\n\n"
                "## Final Synthesis Required\n"
                "No more diagnostic execution."
            ),
        )
    )

    assert output.summary == "NGINX is not confirmed running."
    assert len(calls) == 1
    assert calls[0]["format"] == "json"
    assert calls[0]["options"]["num_predict"] == 6144
    assert calls[0]["options"]["num_ctx"] == 32768

    prompt = calls[0]["messages"][1]["content"]

    assert '"summary":"short conclusion"' in prompt
    assert '"hypotheses":[' not in prompt.split(
        "## Structured Output Contract",
        1,
    )[1].split("JSON rules:", 1)[0]

    asyncio.run(client.close())


def test_normal_reasoning_keeps_existing_generation_limits():
    calls = []

    async def handler(request):
        body = json.loads(request.content)
        calls.append(body)

        return httpx.Response(
            200,
            json={
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(
                        {
                            "summary": "Need evidence.",
                            "confidence": 0.2,
                            "findings": [],
                            "hypotheses": [],
                            "ruled_out": [],
                            "missing_evidence": [],
                            "recommended_next_specialists": [],
                            "diagnostic_tool_requests": [],
                        }
                    )
                },
            },
            request=request,
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
            user_prompt="normal context",
        )
    )

    assert calls[0]["options"]["num_predict"] == 6144
    asyncio.run(client.close())
