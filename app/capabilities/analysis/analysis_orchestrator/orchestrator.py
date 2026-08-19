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


from .exact_reuse_handler import ExactAnalysisReuseHandler
from .generated_analysis_persister import GeneratedAnalysisPersister

class AnalysisOrchestrator:
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
        """
        يربط خدمات التقارير والتحليل والمستودعات الاختيارية بمكوّنات التطبيع والاسترجاع وسياسة إعادة الاستخدام.
        """
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
        self._exact_reuse_handler = ExactAnalysisReuseHandler(
            analysis_repository=self._analysis_repository,
            analysis_source_repository=self._analysis_source_repository,
            retrieval_indexer=self._retrieval_indexer,
            reuse_policy=self._reuse_policy,
            exact_reuse_enabled=self._exact_reuse_enabled,
        )
        self._generated_persister = GeneratedAnalysisPersister(
            analysis_repository=self._analysis_repository,
            analysis_source_repository=self._analysis_source_repository,
            retrieval_indexer=self._retrieval_indexer,
        )



    async def process(
        self,
        *,
        report_id: int,
        server_id: int,
        force: bool = False,
    ) -> int:
        """
        يجلب التقرير ويحسب بصمته، ثم يقرر إعادة الاستخدام أو الاسترجاع المساعد أو التحليل الكامل ويحفظ المصادر وبيانات الأداء.
        """
        start_profile(report_id)
        set_counter("server_id", server_id)
        set_counter("force", force)

        report_fetch_started = perf_counter()
        report = self._report_query_service.get_report(
            report_id
        )
        # يربط التقرير المحفوظ بين القياسات التي جمعتها المراقبة والسياق الذي
        # ستبني عليه مرحلة التحليل والاسترجاع قراراتها اللاحقة.
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


        reused_analysis_id = await self._exact_reuse_handler.try_reuse(
            report_id=report_id,
            server_id=server_id,
            force=force,
            report_fingerprint=report_fingerprint,
            normalized_report=normalized_report,
        )
        if reused_analysis_id is not None:
            return reused_analysis_id

        # يبدأ هنا جمع السياق التاريخي؛ أما تفسير الأدلة فيبقى داخل المحلل،
        # ولا يتحول استرجاع المصادر وحده إلى تشخيص للحالة الحالية.
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

        return await self._generated_persister.persist(
            analysis_id=analysis_id,
            report_id=report_id,
            server_id=server_id,
            normalized_report=normalized_report,
            report_fingerprint=report_fingerprint,
            analysis_decision=analysis_decision,
            retrieved_contexts=retrieved_contexts,
        )
