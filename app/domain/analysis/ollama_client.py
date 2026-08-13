"""Compatibility facade for the relocated Ollama analysis client."""

from app.infrastructure.llm.ollama.analysis_client import (
    OllamaAnalysisClient,
)

__all__ = ["OllamaAnalysisClient"]
