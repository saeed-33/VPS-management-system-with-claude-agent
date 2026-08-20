"""Port required to ingest, chunk, and index knowledge documents."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from app.core.contracts.knowledge_sources.parsed_document import (
    ParsedKnowledgeDocument,
)


class KnowledgeDocumentRepositoryPort(Protocol):
    """Persistence operations required by document-processing capabilities."""

    def get_by_id(self, document_id: int) -> Any | None: ...

    def upsert_parsed(
        self,
        *,
        source_id: int,
        parsed: ParsedKnowledgeDocument,
        content_hash: str,
        fetched_at: datetime,
    ) -> Any: ...

    def mark_failed(
        self,
        *,
        source_id: int,
        canonical_uri: str,
        error_message: str,
    ) -> Any: ...

    def replace_chunks(
        self,
        *,
        document_id: int,
        source_id: int,
        chunks: list[dict[str, Any]],
    ) -> Any: ...

    def update_chunk_embedding(
        self,
        *,
        chunk_id: int,
        embedding: list[float],
        provider: str,
        model: str,
        dimensions: int,
    ) -> None: ...

    def mark_indexed(self, document_id: int) -> Any: ...
