"""
تنسيق مرحلة تقطيع وثيقة المعرفة المحللة.

يتحقق من حالة الوثيقة ووجود النص المحلل، ثم يحول مسودات المقاطع إلى صفوف
مخزنة مع الأحجام والبصمات والبيانات الوصفية.
"""
from __future__ import annotations

from hashlib import sha256

from app.capabilities.knowledge.chunker import (
    StructureAwareKnowledgeChunker,
)
from app.capabilities.knowledge.ingestion_contracts import (
    KnowledgeDocumentStatus,
)
from app.infrastructure.database.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)


class KnowledgeChunkingService:
    """
    ينسق تحويل النص المحلل إلى مقاطع مخزنة وقابلة للفهرسة.
    """
    def __init__(
        self,
        *,
        document_repository: KnowledgeDocumentRepository,
        chunker: StructureAwareKnowledgeChunker,
    ) -> None:
        """
        يربط مستودع وثائق المعرفة ومقسم المحتوى.
        """
        self._document_repository = document_repository
        self._chunker = chunker

    def chunk_document(self, document_id: int):
        """
        يتحقق من الوثيقة المحللة، يقطع نصها، ويستبدل مقاطعها المخزنة مع البصمات والأحجام.
        """
        document = self._document_repository.get_by_id(document_id)

        if document is None:
            raise LookupError("Knowledge document not found.")

        if document.status not in {
            KnowledgeDocumentStatus.PARSED.value,
            KnowledgeDocumentStatus.CHUNKED.value,
        }:
            raise ValueError(
                "Knowledge document must be parsed before chunking."
            )

        metadata = dict(document.document_metadata or {})
        parsed_text = str(metadata.get("parsed_text") or "").strip()

        if not parsed_text:
            raise ValueError(
                "Knowledge document has no parsed_text."
            )

        drafts = self._chunker.chunk_document(
            text=parsed_text,
            metadata=metadata,
        )

        if not drafts:
            raise ValueError(
                "Knowledge chunker produced no chunks."
            )

        rows = [
            {
                "chunk_index": draft.chunk_index,
                "section_title": draft.section_title,
                "page_number": draft.page_number,
                "content": draft.content,
                "character_count": len(draft.content),
                "token_count": draft.token_count,
                "content_hash": sha256(
                    draft.content.encode("utf-8")
                ).hexdigest(),
                "metadata": dict(draft.metadata),
            }
            for draft in drafts
        ]

        return self._document_repository.replace_chunks(
            document_id=document.id,
            source_id=document.source_id,
            chunks=rows,
        )
