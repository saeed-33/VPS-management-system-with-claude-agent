"""Tests for the shared Ollama embedding HTTP client."""
import asyncio

import httpx

from app.infrastructure.llm.ollama.embedding_client import OllamaEmbeddingClient


def test_embedding_client_reuses_http_client_and_closes_it():
    calls = []

    async def handler(request):
        calls.append(request)
        return httpx.Response(
            200,
            json={"embeddings": [[0.1, 0.2, 0.3]]},
            request=request,
        )

    async def exercise():
        client = OllamaEmbeddingClient(
            base_url="http://ollama.test",
            model="test-model",
            dimensions=3,
        )
        await client._client.aclose()
        client._client = httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            base_url="http://ollama.test",
        )

        first = await client.embed("first")
        second = await client.embed("second")

        assert first == second == [0.1, 0.2, 0.3]
        assert len(calls) == 2
        assert all(request.url.path == "/api/embed" for request in calls)

        await client.close()
        assert client._client.is_closed

    asyncio.run(exercise())
