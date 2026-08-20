"""إنشاء عميل reasoning للاختصاصيين ضمن طبقة تركيب التطبيق."""
from __future__ import annotations

from app.core.config import Settings
from app.core.contracts.specialist_reasoning.specialist_reasoning_client import SpecialistReasoningClient

def create_specialist_reasoning_client(
    settings: Settings,
) -> SpecialistReasoningClient:
    """ينشئ عميل reasoning الاختصاصي وفق إعدادات النموذج."""
    from app.infrastructure.llm.ollama.specialist_reasoning_client.client import OllamaSpecialistReasoningClient
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
