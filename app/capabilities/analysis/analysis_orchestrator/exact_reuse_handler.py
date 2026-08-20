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
from app.core.ports.analysis.analysis_repository import AnalysisRepositoryPort
from app.core.ports.analysis.source_repository import AnalysisSourceRepositoryPort
from app.capabilities.monitoring.report_query_service import (
    ReportQueryService,
)

logger = logging.getLogger(__name__)


class ExactAnalysisReuseHandler:
    """يعالج إعادة استخدام التحليل المطابق وفهرسة نسخته الجديدة."""

    def __init__(
        self,
        *,
        analysis_repository: AnalysisRepositoryPort,
        analysis_source_repository: AnalysisSourceRepositoryPort | None,
        retrieval_indexer: RetrievalIndexer | None,
        reuse_policy: AnalysisReusePolicy,
        exact_reuse_enabled: bool,
    ) -> None:
        self._analysis_repository = analysis_repository
        self._analysis_source_repository = analysis_source_repository
        self._retrieval_indexer = retrieval_indexer
        self._reuse_policy = reuse_policy
        self._exact_reuse_enabled = exact_reuse_enabled

    async def try_reuse(
        self,
        *,
        report_id: int,
        server_id: int,
        force: bool,
        report_fingerprint: str,
        normalized_report: str,
    ) -> int | None:
        if (
            self._exact_reuse_enabled
            and not force
        ):
            # تسبق المطابقة الدقيقة الاسترجاع واستدعاء النموذج لأنها تعيد
            # نتيجة قابلة للتتبع بأقل تكلفة عندما تكون البصمة نفسها.
            exact_lookup_started = perf_counter()
            reusable_analysis = (
                self._analysis_repository
                .find_completed_by_fingerprint(
                    server_id=server_id,
                    report_fingerprint=(
                        report_fingerprint
                    ),
                    exclude_report_id=report_id,
                )
            )

            record_timing(
                "exact_lookup_ms",
                (perf_counter() - exact_lookup_started) * 1000,
            )

            exact_decision = self._reuse_policy.decide(
                fingerprint_match=(
                    reusable_analysis is not None
                ),
                historical_context_available=False,
                assisted_enabled=False,
                force=force,
            )

            if (
                reusable_analysis is not None
                and exact_decision.decision
                == AnalysisDecision.REUSE
            ):
                logger.info(
                    "Analysis decision | report_id=%s | "
                    "decision=%s | reason=%s",
                    report_id,
                    exact_decision.decision.value,
                    exact_decision.reason,
                )

                reused = (
                    self._analysis_repository
                    .create_reused_analysis(
                        report_id=report_id,
                        server_id=server_id,
                        source_analysis=(
                            reusable_analysis
                        ),
                        report_fingerprint=(
                            report_fingerprint
                        ),
                        normalized_report=(
                            normalized_report
                        ),
                    )
                )

                logger.info(
                    "Previous analysis reused | "
                    "server_id=%s | report_id=%s | "
                    "analysis_id=%s | "
                    "source_analysis_id=%s",
                    server_id,
                    report_id,
                    reused.id,
                    reusable_analysis.id,
                )

                if (
                    self._analysis_source_repository
                    is not None
                ):
                    try:
                        sources = [
                            {
                                "source_type": (
                                    "current_report"
                                ),
                                "source_report_id": (
                                    report_id
                                ),
                                "source_analysis_id": None,
                                "retrieval_strategy": None,
                                "similarity_score": None,
                                "rank": 0,
                                "title": (
                                    "Current monitoring "
                                    f"report #{report_id}"
                                ),
                                "excerpt": (
                                    normalized_report[:1000]
                                ),
                                "source_metadata": {},
                                "used_in_prompt": False,
                            },
                            {
                                "source_type": (
                                    "reused_analysis"
                                ),
                                "source_report_id": (
                                    reusable_analysis.report_id
                                ),
                                "source_analysis_id": (
                                    reusable_analysis.id
                                ),
                                "retrieval_strategy": (
                                    "exact_fingerprint"
                                ),
                                "similarity_score": 1.0,
                                "rank": 1,
                                "title": (
                                    "Reused analysis "
                                    f"#{reusable_analysis.id}"
                                ),
                                "excerpt": (
                                    reusable_analysis.summary
                                    or ""
                                )[:1000],
                                "source_metadata": {
                                    "health_status": (
                                        reusable_analysis
                                        .health_status
                                    ),
                                },
                                "used_in_prompt": False,
                            },
                        ]

                        (
                            self
                            ._analysis_source_repository
                            .replace_for_analysis(
                                analysis_id=reused.id,
                                sources=sources,
                            )
                        )

                    except Exception:
                        logger.exception(
                            "Reused analysis saved, but "
                            "source recording failed | "
                            "analysis_id=%s",
                            reused.id,
                        )

                if self._retrieval_indexer is not None:
                    try:
                        reuse_index_started = perf_counter()
                        reuse_index_mode = await (
                            self._retrieval_indexer
                            .index_reused_analysis(
                                source_analysis_id=(
                                    reusable_analysis.id
                                ),
                                target_analysis_id=reused.id,
                            )
                        )
                        record_timing(
                            "reuse_index_ms",
                            (
                                perf_counter()
                                - reuse_index_started
                            )
                            * 1000,
                        )
                        set_counter(
                            "reuse_index_mode",
                            reuse_index_mode,
                        )

                    except Exception:
                        logger.exception(
                            "Analysis saved, but retrieval "
                            "indexing failed | "
                            "analysis_id=%s",
                            reused.id,
                        )

                set_counter("decision", "reuse")
                performance_metrics = snapshot()
                try:
                    self._analysis_repository.update_performance_metrics(
                        analysis_id=reused.id,
                        performance_metrics=performance_metrics,
                    )
                finally:
                    clear_profile()

                return reused.id
