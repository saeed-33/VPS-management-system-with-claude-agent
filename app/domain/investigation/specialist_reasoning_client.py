from __future__ import annotations

from abc import ABC, abstractmethod
import json
from typing import Any


from app.shared.config import Settings
from app.shared.dto.specialist_reasoning import (
    SpecialistFinalSynthesisOutput,
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





def create_specialist_reasoning_client(
    settings: Settings,
) -> SpecialistReasoningClient:
    from app.infrastructure.llm.ollama.specialist_reasoning_client import (
        OllamaSpecialistReasoningClient,
    )
    if not settings.llm_enabled:
        raise RuntimeError(
            "LLM analysis is disabled."
        )

    if settings.llm_provider != "ollama":
        raise ValueError(
            "Only LLM_PROVIDER=ollama is supported."
        )

    return OllamaSpecialistReasoningClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=(
            settings.llm_analysis_timeout_seconds
        ),
    )

def __getattr__(name: str):
    if name == 'OllamaSpecialistReasoningClient':
        from app.infrastructure.llm.ollama.specialist_reasoning_client import (
            OllamaSpecialistReasoningClient,
        )
        return OllamaSpecialistReasoningClient

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )

