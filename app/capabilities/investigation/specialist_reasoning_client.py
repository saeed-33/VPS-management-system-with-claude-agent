"""
جزء من Investigation/Specialist لتوجيه التحقيق وجمع Evidence وبناء التشخيص.

الموقع في المعمارية: Application capability / investigation.
يُستدعى بواسطة: MCP أو Analysis workflow.
يعتمد مباشرة على: app.core.config، app.core.contracts.specialist_reasoning.
الحد المعماري: لا يتجاوز Diagnostic Policy؛ Python يتحقق وينفذ collection.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from app.core.config import Settings
from app.core.contracts.specialist_reasoning import SpecialistReasoningClient





def create_specialist_reasoning_client(
    settings: Settings,
) -> SpecialistReasoningClient:
    """
    ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Application capability / investigation.

    تُستدعى عندما يصل workflow إلى create_specialist_reasoning_client؛ المدخلات المهمة: settings.
    تعيد SpecialistReasoningClient أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

    تُستدعى عندما يصل workflow إلى __getattr__؛ المدخلات المهمة: name.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    if name == 'OllamaSpecialistReasoningClient':
        from app.infrastructure.llm.ollama.specialist_reasoning_client import (
            OllamaSpecialistReasoningClient,
        )
        return OllamaSpecialistReasoningClient

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )
