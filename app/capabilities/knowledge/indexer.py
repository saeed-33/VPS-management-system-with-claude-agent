"""
جزء من Knowledge ingestion/indexing/retrieval لتغذية RAG بمصادر قابلة للتتبع.

الموقع في المعمارية: Application capability / knowledge.
يُستدعى بواسطة: أدوات الإدارة أو Retrieval.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.embedding_client، app.capabilities.knowledge.ingestion_contracts، app.infrastructure.database.repositories.knowledge_document_repository.
الحد المعماري: لا يخلط knowledge retrieval مع reasoning.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.capabilities.analysis.retrieval.embedding_client import EmbeddingClient
from app.capabilities.knowledge.ingestion_contracts import (
    KnowledgeDocumentStatus,
)
from app.infrastructure.database.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)


@dataclass(slots=True, frozen=True)
class KnowledgeIndexingResult:
    """
    يمثل KnowledgeIndexingResult مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    document_id: int
    total_chunks: int
    indexed_chunks: int
    skipped_chunks: int
    provider: str
    model: str
    dimensions: int
    status: str


class KnowledgeIndexer:
    """
    يمثل KnowledgeIndexer مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        *,
        document_repository: KnowledgeDocumentRepository,
        embedding_client: EmbeddingClient,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: document_repository، embedding_client.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._document_repository = document_repository
        self._embedding_client = embedding_client

    async def index_document(
        self,
        document_id: int,
        *,
        force: bool = False,
    ) -> KnowledgeIndexingResult:
        """
        ينفذ خطوة من Retrieval أو Knowledge pipeline وينقل provenance ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى index_document؛ المدخلات المهمة: document_id، force.
        تعيد KnowledgeIndexingResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        document = self._document_repository.get_by_id(document_id)

        if document is None:
            raise LookupError("Knowledge document not found.")

        if document.status not in {
            KnowledgeDocumentStatus.CHUNKED.value,
            KnowledgeDocumentStatus.INDEXED.value,
        }:
            raise ValueError(
                "Knowledge document must be chunked before indexing."
            )

        chunks = tuple(document.chunks)

        if not chunks:
            raise ValueError("Knowledge document has no chunks.")

        indexed = 0
        skipped = 0

        for chunk in chunks:
            current = (
                chunk.embedding is not None
                and chunk.embedding_provider
                == self._embedding_client.provider_name
                and chunk.embedding_model
                == self._embedding_client.model_name
                and chunk.embedding_dimensions
                == self._embedding_client.dimensions
            )

            if current and not force:
                skipped += 1
                continue

            text = self._embedding_text(
                section_title=chunk.section_title,
                content=chunk.content,
            )

            embedding = await self._embedding_client.embed(text)

            self._document_repository.update_chunk_embedding(
                chunk_id=chunk.id,
                embedding=embedding,
                provider=self._embedding_client.provider_name,
                model=self._embedding_client.model_name,
                dimensions=self._embedding_client.dimensions,
            )
            indexed += 1

        self._document_repository.mark_indexed(document_id)

        return KnowledgeIndexingResult(
            document_id=document_id,
            total_chunks=len(chunks),
            indexed_chunks=indexed,
            skipped_chunks=skipped,
            provider=self._embedding_client.provider_name,
            model=self._embedding_client.model_name,
            dimensions=self._embedding_client.dimensions,
            status=KnowledgeDocumentStatus.INDEXED.value,
        )

    @staticmethod
    def _embedding_text(
        *,
        section_title: str | None,
        content: str,
    ) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى _embedding_text؛ المدخلات المهمة: section_title، content.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        title = section_title.strip() if section_title else ""

        if title:
            return f"{title}\n\n{content.strip()}"

        return content.strip()
