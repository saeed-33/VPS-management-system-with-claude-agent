"""إنشاء عميل السرد النهائي ضمن طبقة تركيب التطبيق."""
from __future__ import annotations

from app.core.config import Settings
from app.core.contracts.final_diagnosis.final_diagnosis_narrative_client import FinalDiagnosisNarrativeClient

def create_final_diagnosis_narrative_client(
    settings: Settings,
) -> FinalDiagnosisNarrativeClient:
    """ينشئ عميل السرد النهائي وفق إعدادات مزود النموذج."""
    from app.infrastructure.llm.ollama.final_diagnosis_client import (
        OllamaFinalDiagnosisNarrativeClient,
    )
    if not settings.llm_enabled:
        raise RuntimeError(
            "LLM analysis is disabled."
        )

    if settings.llm_provider != "ollama":
        raise ValueError(
            "Only LLM_PROVIDER=ollama is supported."
        )

    return OllamaFinalDiagnosisNarrativeClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=(
            settings.llm_analysis_timeout_seconds
        ),
    )
