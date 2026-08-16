"""
جزء من Retrieval/RAG لتطبيع report أو استرجاع context أو الفهرسة.

الموقع في المعمارية: Application capability / retrieval.
يُستدعى بواسطة: Analysis orchestrator وخدمات الفهرسة.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.embedding_client، app.infrastructure.llm.ollama.embedding_client، app.core.config.
الحد المعماري: ينتهي عند context مع provenance؛ reasoning مسؤولية أعلى.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from app.capabilities.analysis.retrieval.embedding_client import EmbeddingClient
from app.infrastructure.llm.ollama.embedding_client import OllamaEmbeddingClient
from app.core.config import Settings


def create_embedding_client(settings: Settings) -> EmbeddingClient:
    """
    ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Application capability / retrieval.

    تُستدعى عندما يصل workflow إلى create_embedding_client؛ المدخلات المهمة: settings.
    تعيد EmbeddingClient أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    if settings.embedding_provider == "ollama":
        return OllamaEmbeddingClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
            dimensions=settings.embedding_dimensions,
            timeout_seconds=settings.embedding_timeout_seconds,
        )
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
