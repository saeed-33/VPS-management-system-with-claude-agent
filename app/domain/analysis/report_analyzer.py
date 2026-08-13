import json
import logging
from datetime import UTC, datetime
from time import perf_counter

from app.domain.analysis.retrieval.performance_profiler import (
    record_timing,
    set_counter,
)

from app.domain.analysis.llm_client import (
    LLMAnalysisClient,
)
from app.domain.analysis.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
)
from app.domain.analysis.report_serializer import (
    ReportSerializer,
)
from app.infrastructure.database.repositories.analysis_repository import (
    AnalysisRepository,
)
from app.shared.dto.analysis import (
    ReportAnalysisResult,
)
from app.shared.services.report_service import (
    ReportQueryService,
)


logger = logging.getLogger(__name__)


class ReportAnalyzer:
    def __init__(
        self,
        *,
        report_query_service: ReportQueryService,
        analysis_repository: AnalysisRepository,
        llm_client: LLMAnalysisClient,
        max_report_characters: int,
    ) -> None:
        self._report_query_service = (
            report_query_service
        )

        self._analysis_repository = (
            analysis_repository
        )

        self._llm_client = llm_client

        self._serializer = ReportSerializer(
            max_report_characters=(
                max_report_characters
            ),
        )

    @property
    def provider_name(self) -> str:
        return self._llm_client.provider_name

    @property
    def model_name(self) -> str:
        return self._llm_client.model_name

    async def analyze(
        self,
        *,
        report_id: int,
        server_id: int,
        force: bool = False,
        rag_context: list[dict] | None = None,
    ) -> int:
        stored_analysis = (
            self._analysis_repository
            .get_by_report_id(report_id)
        )

        if stored_analysis is None:
            stored_analysis = (
                self._analysis_repository
                .create_pending(
                    report_id=report_id,
                    server_id=server_id,
                    provider_name=(
                        self.provider_name
                    ),
                    model_name=self.model_name,
                )
            )

        elif (
            stored_analysis.status == "completed"
            and not force
        ):
            return stored_analysis.id

        elif force:
            self._analysis_repository.reset_for_retry(
                stored_analysis.id
            )

        analysis_id = stored_analysis.id

        self._analysis_repository.mark_running(
            analysis_id
        )

        started_counter = perf_counter()

        try:
            report = (
                self._report_query_service
                .get_report(report_id)
            )

            serialize_started = perf_counter()
            payload = self._serializer.serialize(
                report
            )
            record_timing(
                "serialization_ms",
                (perf_counter() - serialize_started) * 1000,
            )
            set_counter(
                "current_report_chars",
                len(
                    json.dumps(
                        payload,
                        ensure_ascii=False,
                        default=str,
                    )
                ),
            )
            set_counter(
                "historical_context_count",
                len(rag_context or []),
            )
            set_counter(
                "historical_context_chars",
                len(
                    json.dumps(
                        rag_context or [],
                        ensure_ascii=False,
                        default=str,
                    )
                ),
            )
            set_counter(
                "system_prompt_chars",
                len(SYSTEM_PROMPT),
            )

            prompt_started = perf_counter()
            user_prompt = build_analysis_prompt(
                payload,
                historical_cases=rag_context,
            )
            record_timing(
                "prompt_build_ms",
                (perf_counter() - prompt_started) * 1000,
            )
            set_counter(
                "user_prompt_chars",
                len(user_prompt),
            )

            llm_started = perf_counter()
            result: ReportAnalysisResult = (
                await self._llm_client.analyze_report(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                )
            )
            record_timing(
                "llm_ms",
                (perf_counter() - llm_started) * 1000,
            )

            finished_at = datetime.now(UTC)

            duration_ms = round(
                (
                    perf_counter()
                    - started_counter
                ) * 1000,
                2,
            )

            self._analysis_repository.mark_completed(
                analysis_id=analysis_id,
                result=result,
                finished_at=finished_at,
                duration_ms=duration_ms,
            )

            logger.info(
                "Report analysis completed | "
                "server_id=%s | report_id=%s | "
                "analysis_id=%s | provider=%s | "
                "model=%s",
                server_id,
                report_id,
                analysis_id,
                self.provider_name,
                self.model_name,
            )

            return analysis_id

        except Exception as exc:
            finished_at = datetime.now(UTC)

            duration_ms = round(
                (
                    perf_counter()
                    - started_counter
                ) * 1000,
                2,
            )

            self._analysis_repository.mark_failed(
                analysis_id=analysis_id,
                error_message=(
                    f"{type(exc).__name__}: {exc}"
                ),
                finished_at=finished_at,
                duration_ms=duration_ms,
            )

            logger.exception(
                "Report analysis failed | "
                "server_id=%s | report_id=%s",
                server_id,
                report_id,
            )

            raise