"""
إنشاء مزوّد embedding وفق إعدادات التطبيق.

يتحقق المصنع من اسم المزوّد ويهيئ عميل Ollama بعنوان الخدمة والنموذج والأبعاد
والمهلة المطلوبة.
"""
from app.core.ports.analysis.embedding_client import EmbeddingClient
from app.infrastructure.llm.ollama.embedding_client import OllamaEmbeddingClient
from app.core.config import Settings


def create_embedding_client(settings: Settings) -> EmbeddingClient:
    """
    ينشئ عميل embedding المدعوم من الإعدادات ويرفض المزوّد غير المعروف.
    """
    if settings.embedding_provider == "ollama":
        return OllamaEmbeddingClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
            dimensions=settings.embedding_dimensions,
            timeout_seconds=settings.embedding_timeout_seconds,
        )
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
