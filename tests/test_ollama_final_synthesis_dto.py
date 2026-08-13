import asyncio
import json

import httpx

from app.capabilities.investigation.specialist_reasoning_client import (
    OllamaSpecialistReasoningClient,
)


def test_final_synthesis_minimal_contract_succeeds():
    calls = []

    async def handler(request):
        calls.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(
                        {
                            "summary": "NGINX is not confirmed running.",
                            "confidence": 0.8,
                            "missing_evidence": [
                                "Package installation evidence."
                            ],
                            "recommended_next_specialists": [
                                "systemd-service"
                            ],
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

    output = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt=(
                "context\n\n"
                "## Final Synthesis Required\n"
                "No more Tools."
            ),
        )
    )

    assert output.summary == "NGINX is not confirmed running."
    assert output.findings == []
    assert output.hypotheses == []
    assert output.diagnostic_tool_requests == []
    assert output.recommended_next_specialists == [
        "systemd-service"
    ]
    assert calls[0]["format"] == "json"
    assert calls[0]["options"]["num_ctx"] == 32768
    assert calls[0]["options"]["num_predict"] == 6144

    asyncio.run(client.close())
