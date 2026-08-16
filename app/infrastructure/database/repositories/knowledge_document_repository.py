"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.capabilities.knowledge.ingestion_contracts، app.infrastructure.database.models.knowledge_document، app.infrastructure.database.session، app.core.utils.datetime.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.capabilities.knowledge.ingestion_contracts import (
    KnowledgeDocumentStatus,
    ParsedKnowledgeDocument,
)
from app.infrastructure.database.models.knowledge_document import (
    KnowledgeChunkModel,
    KnowledgeDocumentModel,
)
from app.infrastructure.database.session import SessionLocal
from app.core.utils.datetime import utc_now


class KnowledgeDocumentRepository:
    """
    يمثل KnowledgeDocumentRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه application capabilities
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: session_factory.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._session_factory = session_factory

    def get_by_id(
        self,
        document_id: int,
    ) -> KnowledgeDocumentModel | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_id؛ المدخلات المهمة: document_id.
        تعيد KnowledgeDocumentModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_source_uri؛ المدخلات المهمة: source_id، canonical_uri.
        تعيد KnowledgeDocumentModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى upsert_parsed؛ المدخلات المهمة: source_id، parsed، content_hash، fetched_at.
        تعيد KnowledgeDocumentModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى mark_failed؛ المدخلات المهمة: source_id، canonical_uri، error_message.
        تعيد KnowledgeDocumentModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى replace_chunks؛ المدخلات المهمة: document_id، source_id، chunks.
        تعيد KnowledgeDocumentModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update_chunk_embedding؛ المدخلات المهمة: chunk_id، embedding، provider، model، dimensions.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى mark_indexed؛ المدخلات المهمة: document_id.
        تعيد KnowledgeDocumentModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
