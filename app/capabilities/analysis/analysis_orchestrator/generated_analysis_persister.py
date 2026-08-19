"""
تنسيق قرار تحليل تقرير المراقبة.

يوازن المنسق بين إعادة استخدام تحليل مطابق، والاستفادة من سياق تاريخي مشابه،
وإنشاء تحليل جديد، ثم يسجل مصادر النتيجة وبيانات الأداء اللازمة للتدقيق.
"""
import logging
from time import perf_counter

from app.capabilities.analysis.report_analyzer import (
    ReportAnalyzer,
)
from app.capabilities.analysis.retrieval.report_fingerprint import (
    ReportFingerprintService,
)
from app.capabilities.analysis.retrieval.report_normalizer import (
    ReportNormalizer,
)
from app.capabilities.analysis.retrieval.retrieval_indexer import (
    RetrievalIndexer,
)
from app.capabilities.analysis.retrieval.context_builder import (
    RagContextBuilder,
)
from app.capabilities.analysis.retrieval.rag_retriever import (
    RagRetriever,
)
from app.capabilities.analysis.retrieval.hybrid_retriever.retriever import HybridRetriever
from app.capabilities.analysis.retrieval.reuse_policy.decision import AnalysisDecision
from app.capabilities.analysis.retrieval.reuse_policy.policy import AnalysisReusePolicy
from app.capabilities.analysis.retrieval.performance_profiler import (
    clear_profile,
    record_timing,
    set_counter,
    snapshot,
    start_profile,
)
from app.infrastructure.database.repositories.analysis_repository.repository import AnalysisRepository
from app.infrastructure.database.repositories.analysis_source_repository import (
    AnalysisSourceRepository,
)
from app.capabilities.monitoring.report_query_service import (
    ReportQueryService,
)

logger = logging.getLogger(__name__)


class GeneratedAnalysisPersister:
    """يحفظ التحليل الجديد ومصادره ويفهرسه ويثبت مقاييس الأداء."""

    def __init__(
        self,
        *,
        analysis_repository: AnalysisRepository,
        analysis_source_repository: AnalysisSourceRepository | None,
        retrieval_indexer: RetrievalIndexer | None,
    ) -> None:
        self._analysis_repository = analysis_repository
        self._analysis_source_repository = analysis_source_repository
        self._retrieval_indexer = retrieval_indexer

    async def persist(
        self,
        *,
        analysis_id: int,
        report_id: int,
        server_id: int,
        normalized_report: str,
        report_fingerprint: str,
        analysis_decision,
        retrieved_contexts,
    ) -> int:
        self._analysis_repository.update_retrieval_metadata(
            analysis_id=analysis_id,
            report_fingerprint=report_fingerprint,
            normalized_report=normalized_report,
            analysis_source=(
                "generated_with_context"
                if analysis_decision.decision
                == AnalysisDecision.ASSISTED
                else "generated"
            ),
            reused_from_analysis_id=None,
            retrieval_strategy=(
                retrieved_contexts[0]
                .retrieval_strategy
                if (
                    analysis_decision.decision
                    == AnalysisDecision.ASSISTED
                    and retrieved_contexts
                )
                else None
            ),
            retrieval_score=(
                retrieved_contexts[0].vector_score
                if (
                    analysis_decision.decision
                    == AnalysisDecision.ASSISTED
                    and retrieved_contexts
                    and retrieved_contexts[0].vector_score
                    is not None
                )
                else None
            ),
            llm_called=True,
        )

        if self._analysis_source_repository is not None:
            sources = [
                {
                    "source_type": "current_report",
                    "source_report_id": report_id,
                    "source_analysis_id": None,
                    "retrieval_strategy": None,
                    "similarity_score": None,
                    "rank": 0,
                    "title": (
                        f"Current monitoring report #{report_id}"
                    ),
                    "excerpt": (
                        normalized_report[:1000]
                    ),
                    "source_metadata": {},
                    "used_in_prompt": True,
                },
            ]
            for item in retrieved_contexts:
                sources.append(
                    {
                        "source_type": "similar_report",
                        "source_report_id": item.source_report_id,
                        "source_analysis_id": item.source_analysis_id,
                        "retrieval_strategy": (
                            item.retrieval_strategy
                        ),
                        "similarity_score": item.vector_score,
                        "rank": item.rank,
                        "title": (
                            f"Similar report #{item.source_report_id}"
                        ),
                        "excerpt": (item.summary or "")[:1000],
                        "source_metadata": {
                            "health_status": item.health_status,
                            "vector_score": item.vector_score,
                            "text_score": item.text_score,
                            "vector_rank": item.vector_rank,
                            "text_rank": item.text_rank,
                            "rrf_score": item.score,
                        },
                        "used_in_prompt": True,
                    }
                )
            self._analysis_source_repository.replace_for_analysis(
                analysis_id=analysis_id,
                sources=sources,
            )

        if self._retrieval_indexer is not None:
            try:
                indexing_started = perf_counter()
                await self._retrieval_indexer.index_analysis(
                    analysis_id
                )
                record_timing(
                    "indexing_ms",
                    (perf_counter() - indexing_started) * 1000,
                )
            except Exception:
                logger.exception(
                    "Analysis saved, but retrieval indexing failed | analysis_id=%s",
                    analysis_id,
                )

        performance_metrics = snapshot()
        self._analysis_repository.update_performance_metrics(
            analysis_id=analysis_id,
            performance_metrics=performance_metrics,
        )
        logger.info(
            "Analysis performance | report_id=%s | analysis_id=%s | metrics=%s",
            report_id,
            analysis_id,
            performance_metrics,
        )
        clear_profile()

        logger.info(
            "New LLM analysis indexed | "
            "server_id=%s | report_id=%s | "
            "analysis_id=%s | fingerprint=%s",
            server_id,
            report_id,
            analysis_id,
            report_fingerprint[:12],
        )

        return analysis_id
