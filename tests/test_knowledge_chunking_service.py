from types import SimpleNamespace

from app.agent.investigation.knowledge_chunker import (
    KnowledgeChunkerConfig,
    StructureAwareKnowledgeChunker,
)
from app.agent.investigation.knowledge_chunking_service import (
    KnowledgeChunkingService,
)


class Repository:
    def __init__(self):
        self.document = SimpleNamespace(
            id=7,
            source_id=3,
            status="parsed",
            document_metadata={
                "parsed_text": "CPU diagnostics. " * 100
            },
        )
        self.saved = None

    def get_by_id(self, document_id):
        return self.document if document_id == 7 else None

    def replace_chunks(self, **kwargs):
        self.saved = kwargs
        return SimpleNamespace(
            id=7,
            source_id=3,
            status="chunked",
            character_count=1700,
            chunks=[
                SimpleNamespace(**item)
                for item in kwargs["chunks"]
            ],
        )


def test_chunking_service_persists_chunks():
    repository = Repository()
    service = KnowledgeChunkingService(
        document_repository=repository,
        chunker=StructureAwareKnowledgeChunker(
            KnowledgeChunkerConfig(
                target_chars=300,
                max_chars=450,
                overlap_chars=40,
                min_chars=50,
            )
        ),
    )

    result = service.chunk_document(7)

    assert result.status == "chunked"
    assert repository.saved["document_id"] == 7
    assert repository.saved["chunks"]
    assert all(
        len(item["content_hash"]) == 64
        for item in repository.saved["chunks"]
    )
