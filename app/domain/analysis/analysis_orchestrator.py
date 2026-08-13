import logging
from time import perf_counter

from app.domain.analysis.report_analyzer import (
    ReportAnalyzer,
)
from app.domain.analysis.retrieval.report_fingerprint import (
    ReportFingerprintService,
)
from app.domain.analysis.retrieval.report_normalizer import (
    ReportNormalizer,
)
from app.domain.analysis.retrieval.retrieval_indexer import (
    RetrievalIndexer,
)
from app.domain.analysis.retrieval.context_builder import (
    RagContextBuilder,
)
from app.domain.analysis.retrieval.rag_retriever import (
    RagRetriever,
)
from app.domain.analysis.retrieval.hybrid_retriever import (
    HybridRetriever,
)
from app.domain.analysis.retrieval.reuse_policy import (
    AnalysisDecision,
    AnalysisReusePolicy,
)
from app.domain.analysis.retrieval.performance_profiler import (
    clear_profile,
    record_timing,
    set_counter,
    snapshot,
    start_profile,
)
from app.infrastructure.database.repositories.analysis_repository import (
    AnalysisRepository,
)
from app.infrastructure.database.repositories.analysis_source_repository import (
    AnalysisSourceRepository,
)
from app.shared.services.report_service import (
    ReportQueryService,
)

logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """
    يقرر هل يجب استدعاء LLM أو إعادة استخدام
    تحليل سابق مطابق.
    """

    def __init__(
        self,
        *,
        report_query_service: ReportQueryService,
        analysis_repository: AnalysisRepository,
        report_analyzer: ReportAnalyzer,
        exact_reuse_enabled: bool = True,
        retrieval_indexer: RetrievalIndexer | None = None,
        rag_retriever: RagRetriever | HybridRetriever | None = None,
        rag_context_builder: RagContextBuilder | None = None,
        analysis_source_repository: AnalysisSourceRepository | None = None,
        rag_assisted_enabled: bool = True,
        analysis_reuse_policy: AnalysisReusePolicy | None = None,
    ) -> None:
        self._report_query_service = (
            report_query_service
        )

        self._analysis_repository = (
            analysis_repository
        )

        self._report_analyzer = (
            report_analyzer
        )

        self._exact_reuse_enabled = (
            exact_reuse_enabled
        )

        self._normalizer = ReportNormalizer()
        self._retrieval_indexer = retrieval_indexer
        self._rag_retriever = rag_retriever
        self._rag_context_builder = rag_context_builder
        self._analysis_source_repository = (
            analysis_source_repository
        )
        self._rag_assisted_enabled = rag_assisted_enabled
        self._reuse_policy = (
            analysis_reuse_policy
            or AnalysisReusePolicy()
        )

        self._fingerprint_service = (
            ReportFingerprintService()
        )

    async def process(
        self,
        *,
        report_id: int,
        server_id: int,
        force: bool = False,
    ) -> int:
        start_profile(report_id)
        set_counter("server_id", server_id)
        set_counter("force", force)

        report_fetch_started = perf_counter()
        report = self._report_query_service.get_report(
            report_id
        )
        record_timing(
            "report_fetch_ms",
            (perf_counter() - report_fetch_started) * 1000,
        )

        normalization_started = perf_counter()
        normalized_report = (
            self._normalizer.normalize(report)
        )

        command_set_hash = (
            self._normalizer.command_set_hash(report)
        )
        report_fingerprint = (
            self._fingerprint_service.create(
                normalized_report
            )
        )
        record_timing(
            "normalization_fingerprint_ms",
            (perf_counter() - normalization_started) * 1000,
        )

        if (
            self._exact_reuse_enabled
            and not force
        ):
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

        retrieved_contexts = []
        rag_prompt_context = []

        if (
            not force
            and self._rag_retriever is not None
            and self._rag_context_builder is not None
        ):
            try:
                retrieval_started = perf_counter()
                retrieved_contexts = await (
                    self._rag_retriever.retrieve(
                        normalized_report=normalized_report,
                        server_id=server_id,
                        monitoring_profile_id=(
                            report.monitoring_profile_id
                        ),
                        command_set_hash=command_set_hash,
                        exclude_report_id=report_id,
                    )
                )
                record_timing(
                    "retrieval_total_ms",
                    (perf_counter() - retrieval_started) * 1000,
                )

                context_started = perf_counter()
                rag_prompt_context = (
                    self._rag_context_builder.build(
                        retrieved_contexts
                    )
                )
                record_timing(
                    "context_build_ms",
                    (perf_counter() - context_started) * 1000,
                )
            except Exception:
                logger.exception(
                    "RAG retrieval failed; continuing without "
                    "historical context | report_id=%s",
                    report_id,
                )

        analysis_decision = self._reuse_policy.decide(
            fingerprint_match=False,
            historical_context_available=bool(
                retrieved_contexts
            ),
            assisted_enabled=(
                self._rag_assisted_enabled
            ),
            force=force,
        )

        if (
            analysis_decision.decision
            == AnalysisDecision.FULL
        ):
            retrieved_contexts = []
            rag_prompt_context = []

        logger.info(
            "Analysis decision | report_id=%s | "
            "decision=%s | reason=%s | contexts=%s",
            report_id,
            analysis_decision.decision.value,
            analysis_decision.reason,
            len(retrieved_contexts),
        )

        set_counter(
            "decision",
            analysis_decision.decision.value,
        )
        set_counter(
            "retrieved_contexts",
            len(retrieved_contexts),
        )

        analyzer_started = perf_counter()
        analysis_id = await (
            self._report_analyzer.analyze(
                report_id=report_id,
                server_id=server_id,
                force=force,
                rag_context=rag_prompt_context,
            )
        )

        record_timing(
            "analyzer_total_ms",
            (perf_counter() - analyzer_started) * 1000,
        )

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
