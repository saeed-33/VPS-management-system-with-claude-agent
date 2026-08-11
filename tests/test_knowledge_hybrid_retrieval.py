import asyncio

from app.domain.knowledge.retrieval import (
    KnowledgeHybridRetriever,
)
from app.shared.database.repositories.knowledge_retrieval_repository import (
    KnowledgeSearchRow,
)


class EmbeddingClient:
    provider_name = "test"
    model_name = "test-model"
    dimensions = 3

    async def embed(self, text):
        return [0.1, 0.2, 0.3]


def row(
    chunk_id,
    *,
    score,
    specialist_slugs=(),
    domains=(),
    priority=10,
):
    return KnowledgeSearchRow(
        chunk_id=chunk_id,
        document_id=1,
        source_id=7,
        source_slug=f"source-{chunk_id}",
        source_name="Source",
        source_uri="https://example.com",
        source_priority=priority,
        domains=tuple(domains),
        specialist_slugs=tuple(specialist_slugs),
        document_title="Document",
        canonical_uri="https://example.com/doc",
        section_title="Section",
        page_number=None,
        content=f"Content {chunk_id}",
        score=score,
    )


class Repository:
    def find_by_vector(self, **kwargs):
        return [
            row(
                1,
                score=0.90,
                specialist_slugs=("nginx",),
                domains=("http",),
            ),
            row(
                2,
                score=0.82,
                domains=("http",),
            ),
        ]

    def find_by_full_text(self, **kwargs):
        return [
            row(
                2,
                score=0.50,
                domains=("http",),
            ),
            row(
                1,
                score=0.40,
                specialist_slugs=("nginx",),
                domains=("http",),
            ),
        ]


def test_hybrid_retrieval_fuses_both_branches():
    retriever = KnowledgeHybridRetriever(
        repository=Repository(),
        embedding_client=EmbeddingClient(),
        top_k=2,
    )

    contexts = asyncio.run(
        retriever.retrieve(
            query="reverse proxy",
            specialist_slug="nginx",
            domains=("http",),
        )
    )

    assert len(contexts) == 2
    assert {
        item.retrieval_strategy
        for item in contexts
    } == {"hybrid"}


def test_specialist_scope_boosts_direct_source():
    retriever = KnowledgeHybridRetriever(
        repository=Repository(),
        embedding_client=EmbeddingClient(),
        top_k=2,
    )

    contexts = asyncio.run(
        retriever.retrieve(
            query="reverse proxy",
            specialist_slug="nginx",
            domains=("http",),
        )
    )

    assert contexts[0].chunk_id == 1
    assert contexts[0].matched_specialist is True


class VectorOnlyRepository:
    def find_by_vector(self, **kwargs):
        return [
            row(
                5,
                score=0.88,
                domains=("network",),
            )
        ]

    def find_by_full_text(self, **kwargs):
        return []


def test_vector_only_candidate_is_allowed():
    retriever = KnowledgeHybridRetriever(
        repository=VectorOnlyRepository(),
        embedding_client=EmbeddingClient(),
    )

    contexts = asyncio.run(
        retriever.retrieve(
            query="socket backlog",
            domains=("network",),
        )
    )

    assert len(contexts) == 1
    assert contexts[0].retrieval_strategy == "vector"
