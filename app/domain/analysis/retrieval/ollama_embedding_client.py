"""Compatibility facade for the relocated Ollama embedding client."""

from app.infrastructure.llm.ollama.embedding_client import (
    OllamaEmbeddingClient,
)

__all__ = ["OllamaEmbeddingClient"]
