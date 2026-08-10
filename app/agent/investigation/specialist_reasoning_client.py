from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
import json
from typing import Any

import httpx
from openai import AsyncOpenAI
from pydantic import ValidationError

from app.shared.config import Settings
from app.shared.dto.specialist_reasoning import (
    SpecialistReasoningOutput,
)


class SpecialistReasoningClient(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def reason(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> SpecialistReasoningOutput:
        raise NotImplementedError


class OllamaSpecialistReasoningClient(
    SpecialistReasoningClient
):
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
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

    async def reason(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> SpecialistReasoningOutput:
        schema = SpecialistReasoningOutput.model_json_schema()

        compact_schema = json.dumps(
            schema,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        effective_prompt = (
            user_prompt
            + "\n\nReturn exactly one JSON object matching this schema:\n"
            + compact_schema
            + (
                "\n\nReturn JSON only. Do not use Markdown fences. "
                "Keep all prose concise. Do not restate the supplied context."
            )
        )

        use_schema_format = True
        schema_rejection: str | None = None
        last_error: Exception | None = None
        last_content = ""
        last_done_reason = None
        generation_attempt = 0

        while generation_attempt < 2:
            request_format = (
                schema
                if use_schema_format
                else "json"
            )

            response = await self._client.post(
                "/api/chat",
                json={
                    "model": self._model,
                    "stream": False,
                    "think": False,
                    "keep_alive": "15m",
                    "format": request_format,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": (
                                effective_prompt
                                if generation_attempt == 0
                                else (
                                    effective_prompt
                                    + (
                                        "\n\nThe previous generated "
                                        "response was invalid or incomplete. "
                                        "Return a complete and concise JSON "
                                        "object. Close every quote, bracket, "
                                        "and brace."
                                    )
                                )
                            ),
                        },
                    ],
                    "options": {
                        "temperature": 0,
                        "num_predict": (
                            6144
                            if generation_attempt == 0
                            else 8192
                        ),
                    },
                },
            )

            try:
                response.raise_for_status()

            except httpx.HTTPStatusError as exc:
                if (
                    use_schema_format
                    and exc.response.status_code == 400
                ):
                    schema_rejection = exc.response.text[:2000]
                    use_schema_format = False
                    continue

                detail = (
                    exc.response.text[:2000]
                    if exc.response is not None
                    else ""
                )

                raise RuntimeError(
                    "Ollama specialist request failed "
                    f"with HTTP {exc.response.status_code}: {detail}"
                ) from exc

            body = response.json()
            last_done_reason = body.get("done_reason")

            message = body.get("message")
            if not isinstance(message, dict):
                raise RuntimeError(
                    "Ollama specialist response has no valid message."
                )

            content = message.get("content")
            if not isinstance(content, str):
                raise RuntimeError(
                    "Ollama specialist response has no text content."
                )

            last_content = content
            cleaned = content.strip()

            if cleaned.startswith("```"):
                lines = cleaned.splitlines()
                if (
                    lines
                    and lines[0].strip().lower()
                    in {"```json", "```"}
                ):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()

            try:
                return SpecialistReasoningOutput.model_validate_json(cleaned)

            except ValidationError as exc:
                last_error = exc
                generation_attempt += 1
                use_schema_format = False

        compatibility = (
            (
                " Schema format was rejected by the Ollama server: "
                + schema_rejection
            )
            if schema_rejection
            else ""
        )

        raise RuntimeError(
            "Ollama returned invalid specialist structured output "
            "after 2 generated attempts "
            f"(done_reason={last_done_reason!r})."
            + compatibility
            + " Last content: "
            + last_content[:2000]
        ) from last_error

    async def close(self) -> None:
        await self._client.aclose()


class OpenAISpecialistReasoningClient(
    SpecialistReasoningClient
):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        if not api_key.strip():
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai."
            )

        self._model = model
        self._timeout_seconds = timeout_seconds
        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
        )

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    async def reason(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> SpecialistReasoningOutput:
        response = await asyncio.wait_for(
            self._client.responses.parse(
                model=self._model,
                input=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                text_format=SpecialistReasoningOutput,
            ),
            timeout=self._timeout_seconds,
        )

        if response.output_parsed is None:
            raise RuntimeError(
                "OpenAI returned no parsed specialist result."
            )

        return response.output_parsed


def create_specialist_reasoning_client(
    settings: Settings,
) -> SpecialistReasoningClient:
    if not settings.llm_enabled:
        raise RuntimeError("LLM analysis is disabled.")

    if settings.llm_provider == "ollama":
        return OllamaSpecialistReasoningClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.llm_analysis_timeout_seconds,
        )

    if settings.llm_provider == "openai":
        return OpenAISpecialistReasoningClient(
            api_key=settings.openai_api_key or "",
            model=settings.openai_model,
            timeout_seconds=settings.llm_analysis_timeout_seconds,
        )

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )
