"""
جزء من Analysis لتحويل report إلى analysis مع Retrieval وLLM.

الموقع في المعمارية: Application capability / analysis.
يُستدعى بواسطة: MCP أو مسارات ما بعد Monitoring.
يعتمد مباشرة على: app.capabilities.analysis.llm_client، app.infrastructure.llm.ollama.analysis_client، app.core.config.
الحد المعماري: لا ينفذ SSH أو Investigation أو Remediation.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
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
    """
    ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Application capability / analysis.

    تُستدعى عندما يصل workflow إلى create_llm_analysis_client؛ المدخلات المهمة: settings.
    تعيد LLMAnalysisClient أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
