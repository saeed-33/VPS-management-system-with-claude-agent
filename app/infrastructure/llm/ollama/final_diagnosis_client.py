from __future__ import annotations

import httpx

from app.core.contracts.final_diagnosis import (
    FinalDiagnosisNarrativeClient,
    FinalDiagnosisNarrativeOutput,
)

class OllamaFinalDiagnosisNarrativeClient(
    FinalDiagnosisNarrativeClient
):
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self._model = model
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(
                connect=10.0,
                read=timeout_seconds,
                write=30.0,
                pool=10.0,
            ),
        )

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    async def synthesize(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> FinalDiagnosisNarrativeOutput:
        contract = (
            '{"summary":"brief server-level diagnosis",'
            '"claim_ids":[],"conflict_ids":[],'
            '"operator_notes":[]}'
        )

        response = await self._client.post(
            "/api/chat",
            json={
                "model": self._model,
                "stream": False,
                "think": False,
                "keep_alive": "15m",
                "format": "json",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": (
                            user_prompt
                            + "\n\nReturn exactly this JSON shape:\n"
                            + contract
                        ),
                    },
                ],
                "options": {
                    "temperature": 0,
                    "num_ctx": 32768,
                    "num_predict": 4096,
                },
            },
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = (
                exc.response.text[:2000]
                if exc.response is not None
                else ""
            )
            raise RuntimeError(
                "Ollama final diagnosis request failed "
                f"with HTTP {exc.response.status_code}: {detail}"
            ) from exc

        body = response.json()
        message = body.get("message")

        if not isinstance(message, dict):
            raise RuntimeError(
                "Ollama final diagnosis response "
                "has no valid message."
            )

        content = message.get("content")

        if not isinstance(content, str):
            raise RuntimeError(
                "Ollama final diagnosis response "
                "has no text content."
            )

        return (
            FinalDiagnosisNarrativeOutput
            .model_validate_json(
                content.strip()
            )
        )

    async def close(self) -> None:
        await self._client.aclose()

__all__ = [
    'OllamaFinalDiagnosisNarrativeClient',
]
