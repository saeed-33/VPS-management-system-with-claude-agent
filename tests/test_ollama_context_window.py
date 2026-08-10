import asyncio
import json

import httpx

from app.agent.investigation.specialist_reasoning_client import (
    OllamaSpecialistReasoningClient,
)


VALID = {
    "summary": "Concise result.",
    "confidence": 0.5,
    "findings": [],
    "hypotheses": [],
    "ruled_out": [],
    "missing_evidence": [],
    "recommended_next_specialists": [],
    "diagnostic_tool_requests": [],
}

FINAL_SYNTHESIS_VALID = {
    "summary": "Concise result.",
    "confidence": 0.5,
    "missing_evidence": [],
    "recommended_next_specialists": [],
}


def run_request(user_prompt):
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
                        (
                            FINAL_SYNTHESIS_VALID
                            if "## Final Synthesis Required"
                            in user_prompt
                            else VALID
                        )
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
            user_prompt=user_prompt,
        )
    )
    asyncio.run(client.close())
    return calls[0]


def test_normal_reasoning_uses_32k_context_and_6144_output():
    payload = run_request("normal context")

    assert payload["options"]["num_ctx"] == 32768
    assert payload["options"]["num_predict"] == 6144


def test_final_synthesis_uses_32k_context_and_6144_output():
    payload = run_request(
        "context\n\n"
        "## Final Synthesis Required\n"
        "No more diagnostic execution."
    )

    assert payload["options"]["num_ctx"] == 32768
    assert payload["options"]["num_predict"] == 6144
    assert payload["format"] == "json"
