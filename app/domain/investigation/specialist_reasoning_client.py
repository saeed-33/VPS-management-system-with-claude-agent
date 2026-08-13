"""Compatibility facade for the canonical investigation capability."""
from app.capabilities.investigation.specialist_reasoning_client import *  # noqa: F401,F403
from app.infrastructure.llm.ollama.specialist_reasoning_client import (
    OllamaSpecialistReasoningClient,
)

__all__ = [
    "SpecialistReasoningClient",
    "create_specialist_reasoning_client",
    "OllamaSpecialistReasoningClient",
]
