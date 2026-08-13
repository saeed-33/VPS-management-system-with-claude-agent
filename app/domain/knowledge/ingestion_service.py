from __future__ import annotations

from hashlib import sha256

from app.domain.knowledge.parsers import (
    KnowledgeContentParser,
)
from app.domain.knowledge.source_loader import (
    KnowledgeSourceLoader,
)
from app.infrastructure.database.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.infrastructure.database.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)
from app.shared.utils.datetime import utc_now


class KnowledgeIngestionService:
    def __init__(
        self,
        *,
        source_repository: KnowledgeSourceRepository,
        document_repository: KnowledgeDocumentRepository,
        loader: KnowledgeSourceLoader,
        parser: KnowledgeContentParser,
    ) -> None:
        self._source_repository = source_repository
        self._document_repository = document_repository
        self._loader = loader
        self._parser = parser

    def ingest_source(
        self,
        source_id: int,
    ):
        source = self._source_repository.get_by_id(
            source_id
        )

        if source is None:
            raise LookupError(
                "Knowledge source not found."
            )

        if not source.enabled:
            raise ValueError(
                "Knowledge source is disabled."
            )

        fallback_uri = (
            str(source.source_uri or "").strip()
            or f"inline://knowledge-source/{source.slug}"
        )

        try:
            loaded = self._loader.load(source)
            fetched_at = utc_now()

            parsed = self._parser.parse(
                content=loaded.content,
                canonical_uri=loaded.canonical_uri,
                media_type=loaded.media_type,
                title_hint=loaded.title_hint,
            )

            content_hash = sha256(
                parsed.text.encode("utf-8")
            ).hexdigest()

            return self._document_repository.upsert_parsed(
                source_id=source.id,
                parsed=parsed,
                content_hash=content_hash,
                fetched_at=fetched_at,
            )

        except Exception as exc:
            self._document_repository.mark_failed(
                source_id=source.id,
                canonical_uri=fallback_uri,
                error_message=f"{type(exc).__name__}: {exc}",
            )
            raise
