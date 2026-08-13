"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.knowledge_retrieval_repository import (
    KnowledgeRetrievalRepository,
    KnowledgeSearchRow,
)

__all__ = [
    "KnowledgeRetrievalRepository",
    "KnowledgeSearchRow",
]
