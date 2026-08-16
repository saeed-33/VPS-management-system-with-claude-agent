"""
عملاء Ollama للتحليل والتضمين وتفكير المتخصص وصياغة التشخيص النهائي.
"""

from app.infrastructure.llm.ollama.analysis_client import (
    OllamaAnalysisClient,
)
from app.infrastructure.llm.ollama.embedding_client import (
    OllamaEmbeddingClient,
)

__all__ = [
    "OllamaAnalysisClient",
    "OllamaEmbeddingClient",
]
