import asyncio
from types import SimpleNamespace

from app.domain.knowledge.indexer import (
    KnowledgeIndexer,
)


class EmbeddingClient:
    provider_name = "test"
    model_name = "test-model"
    dimensions = 3

    def __init__(self):
        self.calls = []

    async def embed(self, text):
        self.calls.append(text)
        return [0.1, 0.2, 0.3]


class Repository:
    def __init__(self):
        self.updated = []
        self.marked = None
        self.document = SimpleNamespace(
            id=7,
            status="chunked",
            chunks=[
                SimpleNamespace(
                    id=10,
                    section_title="CPU Scheduling",
                    content="Inspect run queue.",
                    embedding=None,
                    embedding_provider=None,
                    embedding_model=None,
                    embedding_dimensions=None,
                ),
                SimpleNamespace(
                    id=11,
                    section_title=None,
                    content="Inspect load average.",
                    embedding=None,
                    embedding_provider=None,
                    embedding_model=None,
                    embedding_dimensions=None,
                ),
            ],
        )

    def get_by_id(self, document_id):
        return self.document if document_id == 7 else None

    def update_chunk_embedding(self, **kwargs):
        self.updated.append(kwargs)

    def mark_indexed(self, document_id):
        self.marked = document_id


def test_indexer_embeds_all_chunks_and_marks_document():
    repository = Repository()
    client = EmbeddingClient()
    indexer = KnowledgeIndexer(
        document_repository=repository,
        embedding_client=client,
    )

    result = asyncio.run(indexer.index_document(7))

    assert result.total_chunks == 2
    assert result.indexed_chunks == 2
    assert result.skipped_chunks == 0
    assert repository.marked == 7
    assert len(repository.updated) == 2
    assert client.calls[0].startswith(
        "CPU Scheduling\n\n"
    )


def test_indexer_skips_current_embedding():
    repository = Repository()
    chunk = repository.document.chunks[0]
    chunk.embedding = [0.1, 0.2, 0.3]
    chunk.embedding_provider = "test"
    chunk.embedding_model = "test-model"
    chunk.embedding_dimensions = 3

    client = EmbeddingClient()
    indexer = KnowledgeIndexer(
        document_repository=repository,
        embedding_client=client,
    )

    result = asyncio.run(indexer.index_document(7))

    assert result.indexed_chunks == 1
    assert result.skipped_chunks == 1


def test_force_reindexes_current_embedding():
    repository = Repository()

    for chunk in repository.document.chunks:
        chunk.embedding = [0.1, 0.2, 0.3]
        chunk.embedding_provider = "test"
        chunk.embedding_model = "test-model"
        chunk.embedding_dimensions = 3

    client = EmbeddingClient()
    indexer = KnowledgeIndexer(
        document_repository=repository,
        embedding_client=client,
    )

    result = asyncio.run(
        indexer.index_document(
            7,
            force=True,
        )
    )

    assert result.indexed_chunks == 2
    assert result.skipped_chunks == 0
