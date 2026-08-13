from __future__ import annotations

from app.core.config import Settings
from app.core.contracts.specialist_reasoning import SpecialistReasoningClient





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
