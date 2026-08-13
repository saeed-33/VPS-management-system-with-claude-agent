"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)

__all__ = [
    "KnowledgeSourceRepository",
]
