from app.agent.analysis.retrieval.embedding_client import EmbeddingClient
from app.agent.analysis.retrieval.ollama_embedding_client import OllamaEmbeddingClient
from app.shared.config import Settings


def create_embedding_client(settings: Settings) -> EmbeddingClient:
    if settings.embedding_provider == "ollama":
        return OllamaEmbeddingClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
            dimensions=settings.embedding_dimensions,
            timeout_seconds=settings.embedding_timeout_seconds,
        )
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
