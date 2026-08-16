"""
جزء من Knowledge ingestion/indexing/retrieval لتغذية RAG بمصادر قابلة للتتبع.

الموقع في المعمارية: Application capability / knowledge.
يُستدعى بواسطة: أدوات الإدارة أو Retrieval.
يعتمد مباشرة على: app.capabilities.knowledge.chunker، app.capabilities.knowledge.ingestion_contracts، app.infrastructure.database.repositories.knowledge_document_repository.
الحد المعماري: لا يخلط knowledge retrieval مع reasoning.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    يمثل KnowledgeChunkingService مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        *,
        document_repository: KnowledgeDocumentRepository,
        chunker: StructureAwareKnowledgeChunker,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: document_repository، chunker.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._document_repository = document_repository
        self._chunker = chunker

    def chunk_document(self, document_id: int):
        """
        ينفذ خطوة من Retrieval أو Knowledge pipeline وينقل provenance ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى chunk_document؛ المدخلات المهمة: document_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
