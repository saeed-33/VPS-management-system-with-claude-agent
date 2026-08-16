"""
البحث النصي عن تحليلات سابقة مشابهة لتقرير المراقبة.

يستخرج المصطلحات التشغيلية من التقرير المنظم، يمررها إلى بحث النص الكامل، ثم
يعيد المرشحين مع ترتيبهم وحالة التحليل التاريخي.
"""
import json
import logging
from time import perf_counter
from dataclasses import dataclass

from app.infrastructure.database.repositories.retrieval_repository import (
    RetrievalRepository,
)
from app.capabilities.analysis.retrieval.performance_profiler import (
    record_timing,
    set_counter,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class FullTextCandidate:
    """
    يمثل مرشحًا أعاده البحث النصي مع هويته وترتيبه وحالة تحليله التاريخي.
    """
    report_id: int
    analysis_id: int
    rank: float
    health_status: str | None


class FullTextQueryBuilder:
    """
    يستخرج من التقرير الحقول النصية الأكثر فائدة لبناء استعلام البحث الكامل.
    """
    def build(self, normalized_report: str) -> str:
        """
        يفك التقرير المنظم ويجمع رسالة الخطأ وحقول التنفيذ النصية في استعلام محدود الحجم.
        """
        try:
            payload = json.loads(normalized_report)
        except (TypeError, ValueError):
            return normalized_report[:10_000]

        terms: list[str] = []

        report_error = payload.get("error_message")
        if report_error:
            terms.append(str(report_error))

        for execution in payload.get("executions", []):
            for field in (
                "command_name",
                "command_text",
                "error_message",
                "stderr",
            ):
                value = execution.get(field)
                if value:
                    terms.append(str(value))

        return "\n".join(terms).strip()[:10_000]


class FullTextRetriever:
    """
    ينفذ البحث النصي ويحوّل صفوف المستودع إلى مرشحين موحدين للاستخدام في الدمج.
    """
    def __init__(
        self,
        *,
        retrieval_repository: RetrievalRepository,
        query_builder: FullTextQueryBuilder | None = None,
        candidate_limit: int = 20,
        minimum_rank: float = 0.0,
    ) -> None:
        """
        يربط مستودع البحث وباني الاستعلام ويضبط عدد المرشحين وأدنى ترتيب مقبول.
        """
        self._retrieval_repository = retrieval_repository
        self._query_builder = (
            query_builder
            or FullTextQueryBuilder()
        )
        self._candidate_limit = candidate_limit
        self._minimum_rank = minimum_rank

    def retrieve(
        self,
        *,
        normalized_report: str,
        server_id: int,
        monitoring_profile_id: int | None,
        command_set_hash: str | None,
        exclude_report_id: int,
    ) -> list[FullTextCandidate]:
        """
        يبني الاستعلام ويبحث ضمن قيود السيرفر والملف ومجموعة الأوامر ثم يعيد المرشحين المرتبين.
        """
        query_started = perf_counter()
        query_text = self._query_builder.build(
            normalized_report
        )
        record_timing(
            "full_text_query_build_ms",
            (perf_counter() - query_started) * 1000,
        )

        search_started = perf_counter()
        rows = (
            self._retrieval_repository
            .find_by_full_text(
                query_text=query_text,
                server_id=server_id,
                monitoring_profile_id=(
                    monitoring_profile_id
                ),
                command_set_hash=command_set_hash,
                exclude_report_id=exclude_report_id,
                minimum_rank=self._minimum_rank,
                limit=self._candidate_limit,
            )
        )

        record_timing(
            "full_text_search_ms",
            (perf_counter() - search_started) * 1000,
        )
        set_counter(
            "full_text_candidates",
            len(rows),
        )

        candidates = [
            FullTextCandidate(
                report_id=document.report_id,
                analysis_id=document.analysis_id,
                rank=rank,
                health_status=(
                    document.analysis_health_status
                ),
            )
            for document, rank in rows
        ]

        logger.info(
            "Full-text retrieval completed | "
            "server_id=%s | report_id=%s | candidates=%s",
            server_id,
            exclude_report_id,
            len(candidates),
        )

        return candidates
