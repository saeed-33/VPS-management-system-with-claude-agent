"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)

__all__ = [
    "KnowledgeDocumentRepository",
]
