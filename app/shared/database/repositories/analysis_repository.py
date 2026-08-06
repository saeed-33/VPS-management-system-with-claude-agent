from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.shared.database.models.report_analysis import (
    AnalysisJobStatus,
    ReportAnalysisModel,
)
from app.shared.database.session import SessionLocal
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