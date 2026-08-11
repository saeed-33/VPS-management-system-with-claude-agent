from app.domain.analysis.llm_client import (
    LLMAnalysisClient,
)
from app.domain.analysis.ollama_client import (
    OllamaAnalysisClient,
)
from app.domain.analysis.openai_client import (
    OpenAIAnalysisClient,
)
from app.shared.config import Settings


def create_llm_analysis_client(
    settings: Settings,
) -> LLMAnalysisClient:
    if not settings.llm_enabled:
        raise RuntimeError(
            "LLM analysis is disabled."
        )

    if settings.llm_provider == "openai":
        return OpenAIAnalysisClient(
            api_key=settings.openai_api_key or "",
            model=settings.openai_model,
            timeout_seconds=(
                settings
                .llm_analysis_timeout_seconds
            ),
        )

    if settings.llm_provider == "ollama":
        return OllamaAnalysisClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=(
                settings
                .llm_analysis_timeout_seconds
            ),
        )

    raise ValueError(
        f"Unsupported LLM provider: "
        f"{settings.llm_provider}"
    )