import asyncio

from openai import AsyncOpenAI

from app.domain.analysis.llm_client import (
    LLMAnalysisClient,
)
from app.shared.dto.analysis import (
    ReportAnalysisResult,
)


class OpenAIAnalysisClient(LLMAnalysisClient):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        if not api_key.strip():
            raise ValueError(
                "OPENAI_API_KEY is required when "
                "LLM_PROVIDER=openai."
            )

        if not model.strip():
            raise ValueError(
                "OPENAI_MODEL cannot be empty."
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

    async def analyze_report(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> ReportAnalysisResult:
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
                text_format=ReportAnalysisResult,
            ),
            timeout=self._timeout_seconds,
        )

        parsed = response.output_parsed

        if parsed is None:
            raise RuntimeError(
                "OpenAI returned no parsed analysis."
            )

        return parsed

    async def health_check(self) -> None:
        await asyncio.wait_for(
            self._client.responses.create(
                model=self._model,
                input=(
                    "Reply with exactly the word OK."
                ),
                max_output_tokens=10,
            ),
            timeout=self._timeout_seconds,
        )