from __future__ import annotations

import asyncio
from dataclasses import dataclass

from app.domain.analysis.retrieval.embedding_client import EmbeddingClient
from app.shared.database.repositories.knowledge_retrieval_repository import (
    KnowledgeRetrievalRepository,
    KnowledgeSearchRow,
)


@dataclass(slots=True, frozen=True)
class KnowledgeRetrievalContext:
    chunk_id: int
    document_id: int
    source_id: int
    source_slug: str
    source_name: str
    source_uri: str | None
    document_title: str | None
    canonical_uri: str
    section_title: str | None
    page_number: int | None
    content: str
    rank: int
    retrieval_strategy: str
    fusion_score: float
    vector_score: float | None
    full_text_score: float | None
    vector_rank: int | None
    full_text_rank: int | None
    matched_specialist: bool
    matched_domains: tuple[str, ...]
    source_priority: int


@dataclass(slots=True)
class _FusionCandidate:
    row: KnowledgeSearchRow
    vector_rank: int | None = None
    vector_score: float | None = None
    text_rank: int | None = None
    text_score: float | None = None

    def rrf_score(self, rrf_k: int) -> float:
        score = 0.0
        if self.vector_rank is not None:
            score += 1.0 / (rrf_k + self.vector_rank)
        if self.text_rank is not None:
            score += 1.0 / (rrf_k + self.text_rank)
        return score

    @property
    def strategy(self) -> str:
        if self.vector_rank is not None and self.text_rank is not None:
            return "hybrid"
        if self.vector_rank is not None:
            return "vector"
        return "full_text"


class KnowledgeHybridRetriever:
    def __init__(
        self,
        *,
        repository: KnowledgeRetrievalRepository,
        embedding_client: EmbeddingClient,
        vector_candidate_limit: int = 12,
        full_text_candidate_limit: int = 20,
        top_k: int = 6,
        rrf_k: int = 60,
        minimum_vector_score: float = 0.35,
        hnsw_ef_search: int = 100,
    ) -> None:
        self._repository = repository
        self._embedding_client = embedding_client
        self._vector_candidate_limit = vector_candidate_limit
        self._full_text_candidate_limit = full_text_candidate_limit
        self._top_k = top_k
        self._rrf_k = rrf_k
        self._minimum_vector_score = minimum_vector_score
        self._hnsw_ef_search = hnsw_ef_search

    async def retrieve(
        self,
        *,
        query: str,
        specialist_slug: str | None = None,
        domains: tuple[str, ...] = (),
    ) -> list[KnowledgeRetrievalContext]:
        query = query.strip()
        if not query:
            return []

        specialist_slug = (
            specialist_slug.strip().casefold()
            if specialist_slug and specialist_slug.strip()
            else None
        )

        domains = tuple(
            dict.fromkeys(
                value.strip().casefold()
                for value in domains
                if value.strip()
            )
        )

        text_task = asyncio.create_task(
            asyncio.to_thread(
                self._repository.find_by_full_text,
                query_text=query,
                specialist_slug=specialist_slug,
                domains=domains,
                limit=self._full_text_candidate_limit,
            )
        )

        embedding = await self._embedding_client.embed(query)

        vector_rows = self._repository.find_by_vector(
            query_embedding=embedding,
            specialist_slug=specialist_slug,
            domains=domains,
            minimum_similarity=self._minimum_vector_score,
            limit=self._vector_candidate_limit,
            hnsw_ef_search=self._hnsw_ef_search,
        )

        text_rows = await text_task

        candidates: dict[int, _FusionCandidate] = {}

        for rank, row in enumerate(vector_rows, start=1):
            item = candidates.setdefault(
                row.chunk_id,
                _FusionCandidate(row=row),
            )
            item.vector_rank = rank
            item.vector_score = row.score

        for rank, row in enumerate(text_rows, start=1):
            item = candidates.setdefault(
                row.chunk_id,
                _FusionCandidate(row=row),
            )
            item.text_rank = rank
            item.text_score = row.score

        ordered = sorted(
            candidates.values(),
            key=lambda item: (
                self._rerank_score(
                    item=item,
                    specialist_slug=specialist_slug,
                    domains=domains,
                ),
                item.vector_score or 0.0,
                item.text_score or 0.0,
                -item.row.source_priority,
            ),
            reverse=True,
        )

        contexts: list[KnowledgeRetrievalContext] = []

        for final_rank, item in enumerate(
            ordered[: self._top_k],
            start=1,
        ):
            matched_specialist = (
                specialist_slug is not None
                and specialist_slug in item.row.specialist_slugs
            )
            matched_domains = tuple(
                domain
                for domain in domains
                if domain in item.row.domains
            )

            contexts.append(
                KnowledgeRetrievalContext(
                    chunk_id=item.row.chunk_id,
                    document_id=item.row.document_id,
                    source_id=item.row.source_id,
                    source_slug=item.row.source_slug,
                    source_name=item.row.source_name,
                    source_uri=item.row.source_uri,
                    document_title=item.row.document_title,
                    canonical_uri=item.row.canonical_uri,
                    section_title=item.row.section_title,
                    page_number=item.row.page_number,
                    content=item.row.content,
                    rank=final_rank,
                    retrieval_strategy=item.strategy,
                    fusion_score=self._rerank_score(
                        item=item,
                        specialist_slug=specialist_slug,
                        domains=domains,
                    ),
                    vector_score=item.vector_score,
                    full_text_score=item.text_score,
                    vector_rank=item.vector_rank,
                    full_text_rank=item.text_rank,
                    matched_specialist=matched_specialist,
                    matched_domains=matched_domains,
                    source_priority=item.row.source_priority,
                )
            )

        return contexts

    def _rerank_score(
        self,
        *,
        item: _FusionCandidate,
        specialist_slug: str | None,
        domains: tuple[str, ...],
    ) -> float:
        score = item.rrf_score(self._rrf_k)

        if (
            specialist_slug
            and specialist_slug in item.row.specialist_slugs
        ):
            score += 0.0025

        domain_matches = sum(
            1
            for domain in domains
            if domain in item.row.domains
        )
        score += min(domain_matches, 3) * 0.001

        score += 1.0 / (
            100_000 + max(item.row.source_priority, 0)
        )

        return score
