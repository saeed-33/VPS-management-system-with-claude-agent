"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.retrieval_repository import (
    RetrievalRepository,
)

__all__ = [
    "RetrievalRepository",
]
