from app.capabilities.analysis.llm_client import (
    LLMAnalysisClient,
)
from app.infrastructure.llm.ollama.analysis_client import (
    OllamaAnalysisClient,
)
from app.core.config import Settings


def create_llm_analysis_client(
    settings: Settings,
) -> LLMAnalysisClient:
    if not settings.llm_enabled:
        raise RuntimeError(
            "LLM analysis is disabled."
        )

    if settings.llm_provider != "ollama":
        raise ValueError(
            "Only LLM_PROVIDER=ollama is supported."
        )

    return OllamaAnalysisClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=(
            settings.llm_analysis_timeout_seconds
        ),
    )
