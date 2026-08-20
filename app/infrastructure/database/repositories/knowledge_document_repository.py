"""
وثائق المعرفة ومقاطعها وحالة تحليلها وفهرستها.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.core.contracts.knowledge_sources.document_status import KnowledgeDocumentStatus
from app.core.contracts.knowledge_sources.parsed_document import ParsedKnowledgeDocument
from app.infrastructure.database.models.knowledge_document.chunk import KnowledgeChunkModel
from app.infrastructure.database.models.knowledge_document.document import KnowledgeDocumentModel
from app.infrastructure.database.session import SessionLocal
from app.core.utils.datetime import utc_now


class KnowledgeDocumentRepository:
    """
    مسؤول عن دورة وثيقة المعرفة من التحليل إلى المقاطع والفهرسة أو الفشل.
    """
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        """
        يهيئ مستودع وثائق المعرفة ومقاطعها وحالة تحليلها وفهرستها بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
        """
        self._session_factory = session_factory

    def get_by_id(
        self,
        document_id: int,
    ) -> KnowledgeDocumentModel | None:
        """
        يسترجع سجلًا من وثائق المعرفة ومقاطعها وحالة تحليلها وفهرستها بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            model = session.get(
                KnowledgeDocumentModel,
                document_id,
            )

            if model is not None:
                _ = model.chunks

            return model

    def get_by_source_uri(
        self,
        *,
        source_id: int,
        canonical_uri: str,
    ) -> KnowledgeDocumentModel | None:
        """
        يسترجع سجلًا من وثائق المعرفة ومقاطعها وحالة تحليلها وفهرستها بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
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
        """
        ينشئ أو يحدث سجلًا في وثائق المعرفة ومقاطعها وحالة تحليلها وفهرستها ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
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
        """
        ينقل سجلًا من وثائق المعرفة ومقاطعها وحالة تحليلها وفهرستها إلى حالة تشغيلية جديدة مع حفظ سبب الانتقال.
        """
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

    def replace_chunks(
        self,
        *,
        document_id: int,
        source_id: int,
        chunks: list[dict],
    ) -> KnowledgeDocumentModel:
        """
        يستبدل مجموعة عناصر مرتبطة بـوثائق المعرفة ومقاطعها وحالة تحليلها وفهرستها في عملية واحدة تحفظ الحالة الجديدة كاملة.
        """
        with self._session_factory() as session:
            document = session.get(
                KnowledgeDocumentModel,
                document_id,
            )

            if document is None:
                raise LookupError("Knowledge document not found.")

            existing = list(
                session.scalars(
                    select(KnowledgeChunkModel)
                    .where(
                        KnowledgeChunkModel.document_id == document_id
                    )
                ).all()
            )

            for item in existing:
                session.delete(item)

            session.flush()

            for item in chunks:
                session.add(
                    KnowledgeChunkModel(
                        document_id=document_id,
                        source_id=source_id,
                        chunk_index=item["chunk_index"],
                        section_title=item.get("section_title"),
                        page_number=item.get("page_number"),
                        content=item["content"],
                        character_count=item["character_count"],
                        token_count=item.get("token_count"),
                        content_hash=item["content_hash"],
                        chunk_metadata=dict(item.get("metadata") or {}),
                    )
                )

            document.status = KnowledgeDocumentStatus.CHUNKED.value
            document.updated_at = utc_now()

            session.commit()
            session.expire(document, ["chunks"])
            _ = document.chunks
            return document

    def update_chunk_embedding(
        self,
        *,
        chunk_id: int,
        embedding: list[float],
        provider: str,
        model: str,
        dimensions: int,
    ) -> None:
        """
        يحدّث انتقالًا أو إعدادًا في وثائق المعرفة ومقاطعها وحالة تحليلها وفهرستها دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            chunk = session.get(
                KnowledgeChunkModel,
                chunk_id,
            )

            if chunk is None:
                raise LookupError("Knowledge chunk not found.")

            chunk.embedding = embedding
            chunk.embedding_provider = provider
            chunk.embedding_model = model
            chunk.embedding_dimensions = dimensions

            session.commit()

    def mark_indexed(
        self,
        document_id: int,
    ) -> KnowledgeDocumentModel:
        """
        ينقل سجلًا من وثائق المعرفة ومقاطعها وحالة تحليلها وفهرستها إلى حالة تشغيلية جديدة مع حفظ سبب الانتقال.
        """
        with self._session_factory() as session:
            document = session.get(
                KnowledgeDocumentModel,
                document_id,
            )

            if document is None:
                raise LookupError("Knowledge document not found.")

            document.status = KnowledgeDocumentStatus.INDEXED.value
            document.updated_at = utc_now()

            session.commit()
            session.refresh(document)
            _ = document.chunks
            return document
