import json
from typing import Any

import httpx

from app.agent.analysis.llm_client import (
    LLMAnalysisClient,
)
from app.shared.dto.analysis import (
    ReportAnalysisResult,
)


class OllamaAnalysisClient(LLMAnalysisClient):
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        if not base_url.strip():
            raise ValueError(
                "OLLAMA_BASE_URL cannot be empty."
            )

        if not model.strip():
            raise ValueError(
                "OLLAMA_MODEL cannot be empty."
            )

        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

        self._client = httpx.AsyncClient(
            base_url=self._base_url,
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

    async def analyze_report(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> ReportAnalysisResult:
        schema = (
            ReportAnalysisResult
            .model_json_schema()
        )

        payload: dict[str, Any] = {
            "model": self._model,
            "stream": False,
            "think": False,
            "keep_alive": "15m",
            "format": schema,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "options": {
                "temperature": 0,
                "num_predict": 1500,
            },
        }

        try:
            response = await self._client.post(
                "/api/chat",
                json=payload,
            )

            response.raise_for_status()

        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama at "
                f"{self._base_url}. Ensure Ollama "
                "is running."
            ) from exc

        except httpx.ReadTimeout as exc:
            raise RuntimeError(
                "Ollama analysis exceeded the "
                f"{self._timeout_seconds}-second timeout. "
                "Use a smaller model, reduce the report "
                "size, or increase the timeout."
            ) from exc

        except httpx.HTTPStatusError as exc:
            response_text = (
                exc.response.text[:2000]
            )

            raise RuntimeError(
                "Ollama returned HTTP "
                f"{exc.response.status_code}: "
                f"{response_text}"
            ) from exc

        body = response.json()

        message = body.get("message")

        if not isinstance(message, dict):
            raise RuntimeError(
                "Ollama response does not contain "
                "a valid message."
            )

        content = message.get("content")

        if not isinstance(content, str):
            raise RuntimeError(
                "Ollama response does not contain "
                "text content."
            )

        try:
            decoded = json.loads(content)

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Ollama returned invalid JSON. "
                f"Response: {content[:1000]}"
            ) from exc

        return ReportAnalysisResult.model_validate(
            decoded
        )

    async def health_check(self) -> None:
        try:
            response = await self._client.get(
                "/api/tags"
            )

            response.raise_for_status()

        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Ollama is not reachable at "
                f"{self._base_url}."
            ) from exc

        body = response.json()
        models = body.get("models", [])

        available_model_names = {
            model.get("name")
            for model in models
            if isinstance(model, dict)
        }

        if self._model not in available_model_names:
            raise RuntimeError(
                f"Ollama model '{self._model}' "
                "is not installed. Available models: "
                f"{sorted(available_model_names)}"
            )

    async def close(self) -> None:
        await self._client.aclose()