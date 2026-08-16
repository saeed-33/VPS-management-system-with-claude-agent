"""
دمج نتائج البحث المتجهي والنصي والتحقق من توافقها.

يستخدم ترتيب RRF لتوحيد المرشحين، يستبعد الحالات ذات التشابه المتجهي المنخفض
أو التعارض التشغيلي، ثم يعيد أفضل سياق تاريخي مكتمل للتحليل.
"""
import logging
from time import perf_counter
from dataclasses import dataclass

from app.capabilities.analysis.retrieval.full_text_retriever import (
    FullTextRetriever,
)
from app.capabilities.analysis.retrieval.rag_context import (
    RetrievedAnalysisContext,
)
from app.capabilities.analysis.retrieval.rag_retriever import (
    RagRetriever,
)
from app.infrastructure.database.repositories.analysis_repository import (
    AnalysisRepository,
)
from app.capabilities.analysis.retrieval.structured_compatibility import (
    StructuredCompatibilityChecker,
)
from app.infrastructure.database.repositories.retrieval_repository import (
    RetrievalRepository,
)
from app.capabilities.analysis.retrieval.performance_profiler import (
    record_timing,
    set_counter,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _FusionCandidate:
    """
    يجمع ترتيب ودرجات مرشح واحد عبر البحث المتجهي والبحث النصي قبل حساب ترتيبه الهجين.
    """
    analysis_id: int
    report_id: int
    vector_rank: int | None = None
    vector_score: float | None = None
    text_rank: int | None = None
    text_score: float | None = None
    vector_context: RetrievedAnalysisContext | None = None

    def rrf_score(self, rrf_k: int) -> float:
        """
        يحسب درجة Reciprocal Rank Fusion من ترتيب المرشح في كل مصدر بحث متاح.
        """
        score = 0.0

        if self.vector_rank is not None:
            score += 1.0 / (rrf_k + self.vector_rank)

        if self.text_rank is not None:
            score += 1.0 / (rrf_k + self.text_rank)

        return score

    @property
    def strategy(self) -> str:
        """
        يحدد ما إذا كان المرشح جاء من البحث المتجهي أو النصي أو كليهما.
        """
        if (
            self.vector_rank is not None
            and self.text_rank is not None
        ):
            return "hybrid"

        if self.vector_rank is not None:
            return "vector"

        return "full_text"


class HybridRetriever:
    """
    يدمج مصادر الاسترجاع ويتحقق من التوافق ثم يعيد أفضل التحليلات المكتملة كسياق.
    """
    def __init__(
        self,
        *,
        analysis_repository: AnalysisRepository,
        retrieval_repository: RetrievalRepository,
        compatibility_checker: StructuredCompatibilityChecker | None,
        vector_retriever: RagRetriever | None,
        full_text_retriever: FullTextRetriever | None,
        top_k: int = 3,
        rrf_k: int = 60,
        minimum_vector_score: float = 0.82,
    ) -> None:
        """
        يربط مستودعات التحليل والاسترجاع ومصادر البحث وفاحص التوافق ويضبط حدود الدمج.
        """
        if vector_retriever is None and full_text_retriever is None:
            raise ValueError(
                "At least one retrieval source is required."
            )

        self._analysis_repository = analysis_repository
        self._retrieval_repository = retrieval_repository
        self._compatibility_checker = compatibility_checker
        self._vector_retriever = vector_retriever
        self._full_text_retriever = full_text_retriever
        self._top_k = top_k
        self._rrf_k = rrf_k
        self._minimum_vector_score = minimum_vector_score

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
        يجمع المرشحين من البحثين، يرتبهم، يستبعد غير المتوافقين، ويبني أفضل السياقات المكتملة.
        """
        candidates: dict[int, _FusionCandidate] = {}

        if self._vector_retriever is not None:
            hybrid_vector_started = perf_counter()
            vector_contexts = await (
                self._vector_retriever.retrieve(
                    normalized_report=normalized_report,
                    server_id=server_id,
                    monitoring_profile_id=(
                        monitoring_profile_id
                    ),
                    command_set_hash=command_set_hash,
                    exclude_report_id=exclude_report_id,
                )
            )

            record_timing(
                "hybrid_vector_branch_ms",
                (perf_counter() - hybrid_vector_started) * 1000,
            )

            for vector_rank, context in enumerate(
                vector_contexts,
                start=1,
            ):
                candidate = candidates.setdefault(
                    context.source_analysis_id,
                    _FusionCandidate(
                        analysis_id=(
                            context.source_analysis_id
                        ),
                        report_id=context.source_report_id,
                    ),
                )
                candidate.vector_rank = vector_rank
                candidate.vector_score = context.score
                candidate.vector_context = context

        if self._full_text_retriever is not None:
            hybrid_text_started = perf_counter()
            text_candidates = (
                self._full_text_retriever.retrieve(
                    normalized_report=normalized_report,
                    server_id=server_id,
                    monitoring_profile_id=(
                        monitoring_profile_id
                    ),
                    command_set_hash=command_set_hash,
                    exclude_report_id=exclude_report_id,
                )
            )

            record_timing(
                "hybrid_full_text_branch_ms",
                (perf_counter() - hybrid_text_started) * 1000,
            )

            for text_rank, text_candidate in enumerate(
                text_candidates,
                start=1,
            ):
                candidate = candidates.setdefault(
                    text_candidate.analysis_id,
                    _FusionCandidate(
                        analysis_id=text_candidate.analysis_id,
                        report_id=text_candidate.report_id,
                    ),
                )
                candidate.text_rank = text_rank
                candidate.text_score = text_candidate.rank

        fusion_started = perf_counter()
        eligible_candidates = [
            item
            for item in candidates.values()
            if (
                item.vector_score is not None
                and item.vector_score
                >= self._minimum_vector_score
            )
        ]

        ordered = sorted(
            eligible_candidates,
            key=lambda item: (
                item.rrf_score(self._rrf_k),
                item.vector_score or 0.0,
                item.text_score or 0.0,
            ),
            reverse=True,
        )

        record_timing(
            "fusion_sort_ms",
            (perf_counter() - fusion_started) * 1000,
        )
        set_counter(
            "hybrid_eligible_candidates",
            len(eligible_candidates),
        )

        contexts: list[RetrievedAnalysisContext] = []

        accepted_candidates = []
        compatibility_started = perf_counter()

        for candidate in ordered:
            if not self._is_compatible(
                current_normalized_report=normalized_report,
                candidate=candidate,
            ):
                continue

            accepted_candidates.append(candidate)

            if len(accepted_candidates) >= self._top_k:
                break

        record_timing(
            "compatibility_ms",
            (perf_counter() - compatibility_started) * 1000,
        )
        set_counter(
            "hybrid_accepted_candidates",
            len(accepted_candidates),
        )

        for final_rank, candidate in enumerate(
            accepted_candidates,
            start=1,
        ):
            context = self._build_context(
                candidate=candidate,
                final_rank=final_rank,
            )
            if context is not None:
                contexts.append(context)

        logger.info(
            "Hybrid retrieval completed | "
            "server_id=%s | report_id=%s | "
            "candidates=%s | contexts=%s",
            server_id,
            exclude_report_id,
            len(eligible_candidates),
            len(contexts),
        )

        return contexts

    def _is_compatible(
        self,
        *,
        current_normalized_report: str,
        candidate: _FusionCandidate,
    ) -> bool:
        """
        يتحقق من وجود مستند المرشح ويقارن تقريره التاريخي بالتقرير الحالي قبل قبوله.
        """
        if self._compatibility_checker is None:
            return True

        document = (
            self._retrieval_repository
            .get_by_analysis_id(candidate.analysis_id)
        )

        if document is None:
            logger.warning(
                "Hybrid candidate rejected because retrieval "
                "document is missing | analysis_id=%s",
                candidate.analysis_id,
            )
            return False

        result = self._compatibility_checker.check(
            current_normalized_report=current_normalized_report,
            historical_normalized_report=document.normalized_text,
        )

        if not result.compatible:
            logger.info(
                "Hybrid candidate rejected by structured "
                "compatibility | analysis_id=%s | conflicts=%s",
                candidate.analysis_id,
                [
                    {
                        "field": conflict.field,
                        "command_id": conflict.command_id,
                        "current": conflict.current,
                        "historical": conflict.historical,
                    }
                    for conflict in result.conflicts
                ],
            )

        return result.compatible

    def _build_context(
        self,
        *,
        candidate: _FusionCandidate,
        final_rank: int,
    ) -> RetrievedAnalysisContext | None:
        """
        يحمّل التحليل المكتمل ويحوّل المرشح المدمج إلى سياق يحمل الدرجات والاستراتيجية والمحتوى.
        """
        analysis = self._analysis_repository.get_by_id(
            candidate.analysis_id
        )
        if analysis is None or analysis.status != "completed":
            return None

        return RetrievedAnalysisContext(
            source_report_id=candidate.report_id,
            source_analysis_id=candidate.analysis_id,
            score=candidate.rrf_score(self._rrf_k),
            rank=final_rank,
            health_status=analysis.health_status,
            summary=analysis.summary,
            issues=list(analysis.issues or []),
            positive_findings=list(
                analysis.positive_findings or []
            ),
            recommended_actions=list(
                analysis.recommended_actions or []
            ),
            retrieval_strategy=candidate.strategy,
            vector_score=candidate.vector_score,
            text_score=candidate.text_score,
            vector_rank=candidate.vector_rank,
            text_rank=candidate.text_rank,
        )
