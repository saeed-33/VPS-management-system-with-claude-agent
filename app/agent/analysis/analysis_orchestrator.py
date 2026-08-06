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
from app.shared.database.repositories.analysis_repository import (
    AnalysisRepository,
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

                return reused.id

        analysis_id = await (
            self._report_analyzer.analyze(
                report_id=report_id,
                server_id=server_id,
                force=force,
            )
        )

        self._analysis_repository.update_retrieval_metadata(
            analysis_id=analysis_id,
            report_fingerprint=report_fingerprint,
            normalized_report=normalized_report,
            analysis_source="generated",
            reused_from_analysis_id=None,
            retrieval_strategy=None,
            retrieval_score=None,
            llm_called=True,
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
