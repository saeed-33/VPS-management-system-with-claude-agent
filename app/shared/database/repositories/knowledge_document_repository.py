from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.agent.investigation.knowledge_ingestion_contracts import (
    KnowledgeDocumentStatus,
    ParsedKnowledgeDocument,
)
from app.shared.database.models.knowledge_document import (
    KnowledgeDocumentModel,
)
from app.shared.database.session import SessionLocal
from app.shared.utils.datetime import utc_now


class KnowledgeDocumentRepository:
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        self._session_factory = session_factory

    def get_by_source_uri(
        self,
        *,
        source_id: int,
        canonical_uri: str,
    ) -> KnowledgeDocumentModel | None:
        with self._session_factory() as session:
            return session.scalar(
                select(KnowledgeDocumentModel)
                .where(
                    KnowledgeDocumentModel.source_id == source_id,
                    KnowledgeDocumentModel.canonical_uri == canonical_uri,
                )
            )

    def upsert_parsed(
        self,
        *,
        source_id: int,
        parsed: ParsedKnowledgeDocument,
        content_hash: str,
        fetched_at,
    ) -> KnowledgeDocumentModel:
        with self._session_factory() as session:
            model = session.scalar(
                select(KnowledgeDocumentModel)
                .where(
                    KnowledgeDocumentModel.source_id == source_id,
                    KnowledgeDocumentModel.canonical_uri == parsed.canonical_uri,
                )
            )

            if model is None:
                model = KnowledgeDocumentModel(
                    source_id=source_id,
                    canonical_uri=parsed.canonical_uri,
                )
                session.add(model)

            model.title = parsed.title
            model.media_type = parsed.media_type
            model.status = KnowledgeDocumentStatus.PARSED.value
            model.content_hash = content_hash
            model.parser_name = parsed.parser_name
            model.parser_version = parsed.parser_version
            model.page_count = parsed.page_count
            model.character_count = len(parsed.text)
            model.error_message = None
            model.document_metadata = {
                **dict(parsed.metadata),
                "parsed_text": parsed.text,
            }
            model.fetched_at = fetched_at
            model.parsed_at = utc_now()
            model.updated_at = utc_now()

            session.commit()
            session.refresh(model)
            return model

    def mark_failed(
        self,
        *,
        source_id: int,
        canonical_uri: str,
        error_message: str,
    ) -> KnowledgeDocumentModel:
        with self._session_factory() as session:
            model = session.scalar(
                select(KnowledgeDocumentModel)
                .where(
                    KnowledgeDocumentModel.source_id == source_id,
                    KnowledgeDocumentModel.canonical_uri == canonical_uri,
                )
            )

            if model is None:
                model = KnowledgeDocumentModel(
                    source_id=source_id,
                    canonical_uri=canonical_uri,
                )
                session.add(model)

            model.status = KnowledgeDocumentStatus.FAILED.value
            model.error_message = error_message[:4000]
            model.updated_at = utc_now()

            session.commit()
            session.refresh(model)
            return model
