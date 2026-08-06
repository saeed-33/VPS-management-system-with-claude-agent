import logging

from app.agent.analysis.report_analyzer import (
    ReportAnalyzer,
)
from app.agent.analysis.retrieval.report_fingerprint import (
    ReportFingerprintService,
)
from app.agent.analysis.retrieval.report_normalizer import (
    ReportNormalizer,
)
from app.agent.analysis.retrieval.retrieval_indexer import (
    RetrievalIndexer,
)
from app.agent.analysis.retrieval.context_builder import (
    RagContextBuilder,
)
from app.agent.analysis.retrieval.rag_retriever import (
    RagRetriever,
)
from app.shared.database.repositories.analysis_repository import (
    AnalysisRepository,
)
from app.shared.database.repositories.analysis_source_repository import (
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
        rag_retriever: RagRetriever | None = None,
        rag_context_builder: RagContextBuilder | None = None,
        analysis_source_repository: AnalysisSourceRepository | None = None,
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
        report = self._report_query_service.get_report(
            report_id
        )

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

        if (
            self._exact_reuse_enabled
            and not force
        ):
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

            if reusable_analysis is not None:
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
                        await (
                            self._retrieval_indexer
                            .index_analysis(
                                reused.id
                            )
                        )

                    except Exception:
                        logger.exception(
                            "Analysis saved, but retrieval "
                            "indexing failed | "
                            "analysis_id=%s",
                            reused.id,
                        )

                return reused.id

        retrieved_contexts = []
        rag_prompt_context = []

        if (
            self._rag_retriever is not None
            and self._rag_context_builder is not None
        ):
            try:
                retrieved_contexts = await (
                    self._rag_retriever.retrieve(
                        normalized_report=normalized_report,            server_id=server_id,
                        monitoring_profile_id=(
                            report.monitoring_profile_id
                        ),
                        command_set_hash=command_set_hash,
                        exclude_report_id=report_id,
                    )
                )
                rag_prompt_context = (
                    self._rag_context_builder.build(
                        retrieved_contexts
                    )
                )
            except Exception:
                logger.exception(
                    "RAG retrieval failed; continuing without "
                    "historical context | report_id=%s",
                    report_id,
                )

        analysis_id = await (
            self._report_analyzer.analyze(
                report_id=report_id,
                server_id=server_id,
                force=force,
                rag_context=rag_prompt_context,
            )
        )

        self._analysis_repository.update_retrieval_metadata(
            analysis_id=analysis_id,
            report_fingerprint=report_fingerprint,
            normalized_report=normalized_report,
            analysis_source="generated",
            reused_from_analysis_id=None,
            retrieval_strategy="vector"
            if retrieved_contexts
            else None,
            retrieval_score=(
                retrieved_contexts[0].score
                if retrieved_contexts
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
                        "retrieval_strategy": "vector",
                        "similarity_score": item.score,
                        "rank": item.rank,
                        "title": (
                            f"Similar report #{item.source_report_id}"
                        ),
                        "excerpt": (item.summary or "")[:1000],
                        "source_metadata": {
                            "health_status": item.health_status,
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
                await self._retrieval_indexer.index_analysis(
                    analysis_id
                )
            except Exception:
                logger.exception(
                    "Analysis saved, but retrieval indexing failed | analysis_id=%s",
                    analysis_id,
                )

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
