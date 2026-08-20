"""Port required to search indexed knowledge chunks."""
from __future__ import annotations

from typing import Protocol

from app.core.contracts.knowledge_sources.knowledge_search_row import (
    KnowledgeSearchRow,
)


class KnowledgeRetrievalRepositoryPort(Protocol):
    """Search operations required by the hybrid knowledge retriever."""

    def find_by_vector(
        self,
        *,
        query_embedding: list[float],
        specialist_slug: str | None,
        domains: tuple[str, ...],
        minimum_similarity: float,
        limit: int,
        hnsw_ef_search: int,
    ) -> list[KnowledgeSearchRow]: ...

    def find_by_full_text(
        self,
        *,
        query_text: str,
        specialist_slug: str | None,
        domains: tuple[str, ...],
        limit: int,
    ) -> list[KnowledgeSearchRow]: ...
