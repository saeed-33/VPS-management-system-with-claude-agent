"""
استرجاع تحليلات تاريخية بالبحث المتجهي.

يحوّل التقرير الحالي إلى embedding، يبحث عن أقرب المستندات ضمن حدود السيرفر
والملف ومجموعة الأوامر، ثم يحمّل التحليلات المكتملة كسياق قابل للتدقيق.
"""
import logging
from time import perf_counter

from app.capabilities.analysis.retrieval.embedding_client import EmbeddingClient
from app.capabilities.analysis.retrieval.rag_context import RetrievedAnalysisContext
from app.infrastructure.database.repositories.analysis_repository import AnalysisRepository
from app.infrastructure.database.repositories.retrieval_repository import RetrievalRepository
from app.capabilities.analysis.retrieval.performance_profiler import (
    record_timing,
    set_counter,
)

logger = logging.getLogger(__name__)


class RagRetriever:
    """
    ينفذ البحث المتجهي ويحوّل المستندات القريبة إلى سياقات تحليلية مكتملة.
    """
    def __init__(
        self,
        *,
        embedding_client: EmbeddingClient,
        retrieval_repository: RetrievalRepository,
        analysis_repository: AnalysisRepository,
        top_k: int = 3,
        minimum_score: float = 0.72,
        hnsw_ef_search: int = 100,
    ) -> None:
        """
        يربط عميل embedding ومستودعات المستندات والتحليلات ويضبط حدود البحث المتجهي.
        """
        self._embedding_client = embedding_client
        self._retrieval_repository = retrieval_repository
        self._analysis_repository = analysis_repository
        self._top_k = top_k
        self._minimum_score = minimum_score
        self._hnsw_ef_search = hnsw_ef_search

    async def retrieve(
        self,
        *,
        normalized_report: str,
        server_id: int,
        monitoring_profile_id: int | None,
        command_set_hash: str | None,
        exclude_report_id: int,
    ) -> list[RetrievedAnalysisContext]:
        """
        ينتج embedding للتقرير، يبحث عن أقرب المرشحين، ويحمّل التحليلات المكتملة كسياقات تاريخية.
        """
        embedding_started = perf_counter()
        embedding = await self._embedding_client.embed(
            normalized_report
        )
        record_timing(
            "embedding_ms",
            (perf_counter() - embedding_started) * 1000,
        )

        vector_search_started = perf_counter()
        candidates = self._retrieval_repository.find_similar(
            server_id=server_id,
            monitoring_profile_id=monitoring_profile_id,
            command_set_hash=command_set_hash,
            embedding=embedding,
            exclude_report_id=exclude_report_id,
            minimum_score=self._minimum_score,
            limit=self._top_k,
            hnsw_ef_search=self._hnsw_ef_search,
        )

        record_timing(
            "vector_search_ms",
            (perf_counter() - vector_search_started) * 1000,
        )
        set_counter(
            "vector_candidates",
            len(candidates),
        )

        contexts: list[RetrievedAnalysisContext] = []
        hydration_started = perf_counter()

        for rank, (document, score) in enumerate(
            candidates,
            start=1,
        ):
            analysis = self._analysis_repository.get_by_id(
                document.analysis_id
            )
            if analysis is None or analysis.status != "completed":
                continue

            contexts.append(
                RetrievedAnalysisContext(
                    source_report_id=document.report_id,
                    source_analysis_id=document.analysis_id,
                    score=score,
                    rank=rank,
                    health_status=analysis.health_status,
                    summary=analysis.summary,
                    issues=list(analysis.issues or []),
                    positive_findings=list(
                        analysis.positive_findings or []
                    ),
                    recommended_actions=list(
                        analysis.recommended_actions or []
                    ),
                )
            )

        record_timing(
            "vector_context_hydration_ms",
            (perf_counter() - hydration_started) * 1000,
        )

        logger.info(
            "RAG retrieval completed | server_id=%s | "
            "exclude_report_id=%s | contexts=%s",
            server_id,
            exclude_report_id,
            len(contexts),
        )
        return contexts
