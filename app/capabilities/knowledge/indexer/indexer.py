"""فهرسة مقاطع المعرفة باستخدام embeddings."""
from __future__ import annotations
from app.core.ports.analysis.embedding_client import EmbeddingClient
from app.core.contracts.knowledge_sources.document_status import KnowledgeDocumentStatus
from app.core.ports.knowledge.document_repository import KnowledgeDocumentRepositoryPort
from .result import KnowledgeIndexingResult

class KnowledgeIndexer:
    """
    ينشئ embeddings لمقاطع وثيقة المعرفة ويحدث حالتها في المستودع.
    """
    def __init__(
        self,
        *,
        document_repository: KnowledgeDocumentRepositoryPort,
        embedding_client: EmbeddingClient,
    ) -> None:
        """
        يربط مستودع الوثائق وعميل embedding المستخدم لفهرسة المقاطع.
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
        يفهرس المقاطع الجديدة أو يجبر إعادة الفهرسة، ثم يعيد ملخص عدد المقاطع وحالة الوثيقة.
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
        يضم عنوان القسم إلى محتوى المقطع لبناء النص الذي سيحوّل إلى embedding.
        """
        title = section_title.strip() if section_title else ""

        if title:
            return f"{title}\n\n{content.strip()}"

        return content.strip()
