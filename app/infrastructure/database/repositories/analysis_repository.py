from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.shared.database.models.report_analysis import (
    AnalysisJobStatus,
    ReportAnalysisModel,
)
from app.infrastructure.database.session import SessionLocal
from app.shared.dto.analysis import (
    ReportAnalysisResult,
)
from app.shared.utils.datetime import utc_now


class AnalysisRepository:
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        self._session_factory = session_factory

    def get_by_id(
        self,
        analysis_id: int,
    ) -> ReportAnalysisModel | None:
        with self._session_factory() as session:
            return session.get(
                ReportAnalysisModel,
                analysis_id,
            )

    def get_by_report_id(
        self,
        report_id: int,
    ) -> ReportAnalysisModel | None:
        with self._session_factory() as session:
            statement = select(
                ReportAnalysisModel
            ).where(
                ReportAnalysisModel.report_id
                == report_id
            )

            return session.scalar(statement)

    def create_pending(
        self,
        *,
        report_id: int,
        server_id: int,
        provider_name: str,
        model_name: str,
    ) -> ReportAnalysisModel:
        model = ReportAnalysisModel(
            report_id=report_id,
            server_id=server_id,
            provider_name=provider_name,
            model_name=model_name,
            status=AnalysisJobStatus.PENDING.value,
        )

        with self._session_factory() as session:
            session.add(model)

            try:
                session.commit()
            except IntegrityError:
                session.rollback()

                existing = session.scalar(
                    select(ReportAnalysisModel).where(
                        ReportAnalysisModel.report_id
                        == report_id
                    )
                )

                if existing is None:
                    raise

                return existing

            session.refresh(model)

            return model

    def mark_running(
        self,
        analysis_id: int,
    ) -> None:
        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                raise ValueError(
                    f"Analysis {analysis_id} not found."
                )

            model.status = (
                AnalysisJobStatus.RUNNING.value
            )

            model.started_at = utc_now()
            model.finished_at = None
            model.analysis_error = None
            model.attempts += 1
            model.updated_at = utc_now()

            session.commit()

    def mark_completed(
        self,
        *,
        analysis_id: int,
        result: ReportAnalysisResult,
        finished_at: datetime,
        duration_ms: float,
    ) -> None:
        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                raise ValueError(
                    f"Analysis {analysis_id} not found."
                )

            model.status = (
                AnalysisJobStatus.COMPLETED.value
            )

            model.health_status = (
                result.health_status.value
            )

            model.summary = result.summary

            model.issues = [
                issue.model_dump(
                    mode="json"
                )
                for issue in result.issues
            ]

            model.positive_findings = (
                result.positive_findings
            )

            model.recommended_actions = (
                result.recommended_actions
            )

            model.analysis_error = None
            model.finished_at = finished_at
            model.duration_ms = duration_ms
            model.updated_at = utc_now()

            session.commit()

    def mark_failed(
        self,
        *,
        analysis_id: int,
        error_message: str,
        finished_at: datetime,
        duration_ms: float,
    ) -> None:
        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                return

            model.status = (
                AnalysisJobStatus.FAILED.value
            )

            model.analysis_error = error_message
            model.finished_at = finished_at
            model.duration_ms = duration_ms
            model.updated_at = utc_now()

            session.commit()

    def reset_for_retry(
        self,
        analysis_id: int,
    ) -> None:
        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                raise ValueError(
                    f"Analysis {analysis_id} not found."
                )

            model.status = (
                AnalysisJobStatus.PENDING.value
            )

            model.health_status = None
            model.summary = None
            model.issues = []
            model.positive_findings = []
            model.recommended_actions = []
            model.analysis_error = None
            model.started_at = None
            model.finished_at = None
            model.duration_ms = None
            model.updated_at = utc_now()

            session.commit()

    def list_pending_or_running(
        self,
    ) -> list[ReportAnalysisModel]:
        with self._session_factory() as session:
            statement = (
                select(ReportAnalysisModel)
                .where(
                    ReportAnalysisModel.status.in_(
                        [
                            AnalysisJobStatus.PENDING.value,
                            AnalysisJobStatus.RUNNING.value,
                        ]
                    )
                )
                .order_by(
                    ReportAnalysisModel.created_at
                )
            )

            return list(
                session.scalars(statement).all()
            )

    def find_completed_by_fingerprint(
        self,
        *,
        server_id: int,
        report_fingerprint: str,
        exclude_report_id: int | None = None,
    ) -> ReportAnalysisModel | None:
        with self._session_factory() as session:
            statement = (
                select(ReportAnalysisModel)
                .where(
                    ReportAnalysisModel.server_id
                    == server_id,
                    ReportAnalysisModel.report_fingerprint
                    == report_fingerprint,
                    ReportAnalysisModel.status
                    == AnalysisJobStatus.COMPLETED.value,
                    ReportAnalysisModel.health_status
                    .is_not(None),
                )
                .order_by(
                    ReportAnalysisModel.finished_at.desc(),
                    ReportAnalysisModel.id.desc(),
                )
            )

            if exclude_report_id is not None:
                statement = statement.where(
                    ReportAnalysisModel.report_id
                    != exclude_report_id
                )

            return session.scalar(
                statement.limit(1)
            )

    def update_retrieval_metadata(
        self,
        *,
        analysis_id: int,
        report_fingerprint: str,
        normalized_report: str,
        analysis_source: str = "generated",
        reused_from_analysis_id: int | None = None,
        retrieval_strategy: str | None = None,
        retrieval_score: float | None = None,
        llm_called: bool = True,
    ) -> None:
        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                raise ValueError(
                    f"Analysis {analysis_id} was not found."
                )

            model.report_fingerprint = (
                report_fingerprint
            )

            model.normalized_report = (
                normalized_report
            )

            model.analysis_source = analysis_source

            model.reused_from_analysis_id = (
                reused_from_analysis_id
            )

            model.retrieval_strategy = (
                retrieval_strategy
            )

            model.retrieval_score = retrieval_score
            model.llm_called = llm_called
            model.updated_at = utc_now()

            session.commit()

    def update_performance_metrics(
        self,
        *,
        analysis_id: int,
        performance_metrics: dict,
    ) -> None:
        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                raise ValueError(
                    f"Analysis {analysis_id} was not found."
                )

            model.performance_metrics = performance_metrics
            model.updated_at = utc_now()

            session.commit()

    def create_reused_analysis(
        self,
        *,
        report_id: int,
        server_id: int,
        source_analysis: ReportAnalysisModel,
        report_fingerprint: str,
        normalized_report: str,
    ) -> ReportAnalysisModel:
        now = utc_now()

        model = ReportAnalysisModel(
            report_id=report_id,
            server_id=server_id,
            provider_name=(
                source_analysis.provider_name
            ),
            model_name=source_analysis.model_name,
            status=AnalysisJobStatus.COMPLETED.value,
            health_status=(
                source_analysis.health_status
            ),
            summary=source_analysis.summary,
            issues=list(
                source_analysis.issues or []
            ),
            positive_findings=list(
                source_analysis.positive_findings
                or []
            ),
            recommended_actions=list(
                source_analysis.recommended_actions
                or []
            ),
            analysis_error=None,
            started_at=now,
            finished_at=now,
            duration_ms=0.0,
            attempts=0,
            report_fingerprint=(
                report_fingerprint
            ),
            normalized_report=(
                normalized_report
            ),
            analysis_source="reused",
            reused_from_analysis_id=(
                source_analysis.id
            ),
            retrieval_strategy=(
                "exact_fingerprint"
            ),
            retrieval_score=1.0,
            llm_called=False,
        )

        with self._session_factory() as session:
            session.add(model)

            try:
                session.commit()

            except IntegrityError:
                session.rollback()

                existing = session.scalar(
                    select(
                        ReportAnalysisModel
                    ).where(
                        ReportAnalysisModel.report_id
                        == report_id
                    )
                )

                if existing is None:
                    raise

                return existing

            session.refresh(model)

            return model