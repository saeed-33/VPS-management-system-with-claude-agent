from sqlalchemy import func, select
from sqlalchemy.orm import (
    selectinload,
    sessionmaker,
)

from app.shared.dto.reports import MonitoringReportData
from app.shared.database.models.command_execution import (
    CommandExecutionModel,
)
from app.shared.database.models.monitoring_report import (
    MonitoringReportModel,
)
from app.shared.database.models.server import (
    ServerModel,
)
from app.shared.database.session import SessionLocal


class ReportRepository:
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        self._session_factory = session_factory

    def create(
        self,
        report: MonitoringReportData,
    ) -> int:
        report_model = MonitoringReportModel(
            server_id=report.server_id,
            status=report.status.value,
            started_at=report.started_at,
            finished_at=report.finished_at,
            duration_ms=report.duration_ms,
            connection_successful=(
                report.connection_successful
            ),
            commands_total=report.commands_total,
            commands_succeeded=(
                report.commands_succeeded
            ),
            commands_failed=(
                report.commands_failed
            ),
            error_message=report.error_message,
        )

        for execution in report.executions:
            execution_model = CommandExecutionModel(
                command_id=execution.command_id,
                command_name=execution.command_name,
                command_text=execution.command_text,
                execution_order=(
                    execution.execution_order
                ),
                success=execution.success,
                exit_status=execution.exit_status,
                stdout=execution.stdout,
                stderr=execution.stderr,
                error_message=(
                    execution.error_message
                ),
                fingerprint_strategy=(
                    execution.fingerprint_strategy
                ),
                fingerprint_config=(
                    execution.fingerprint_config
                ),
                started_at=execution.started_at,
                finished_at=execution.finished_at,
                duration_ms=execution.duration_ms,
            )

            report_model.executions.append(
                execution_model
            )

        with self._session_factory() as session:
            session.add(report_model)
            session.commit()
            session.refresh(report_model)

            return report_model.id

    def get_by_id(
        self,
        report_id: int,
    ) -> MonitoringReportModel | None:
        with self._session_factory() as session:
            statement = (
                select(MonitoringReportModel)
                .options(
                    selectinload(
                        MonitoringReportModel.executions
                    )
                )
                .where(
                    MonitoringReportModel.id
                    == report_id
                )
            )

            return session.scalar(statement)

    def list_reports(
        self,
        *,
        server_id: int | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[
        tuple[MonitoringReportModel, ServerModel]
    ]:
        with self._session_factory() as session:
            statement = (
                select(
                    MonitoringReportModel,
                    ServerModel,
                )
                .join(
                    ServerModel,
                    ServerModel.id
                    == MonitoringReportModel.server_id,
                )
                .order_by(
                    MonitoringReportModel.id.desc()
                )
                .offset(offset)
                .limit(limit)
            )

            if server_id is not None:
                statement = statement.where(
                    MonitoringReportModel.server_id
                    == server_id
                )

            if status is not None:
                statement = statement.where(
                    MonitoringReportModel.status
                    == status
                )

            return list(
                session.execute(statement).all()
            )

    def count_reports(
        self,
        *,
        server_id: int | None = None,
        status: str | None = None,
    ) -> int:
        with self._session_factory() as session:
            statement = select(
                func.count(
                    MonitoringReportModel.id
                )
            )

            if server_id is not None:
                statement = statement.where(
                    MonitoringReportModel.server_id
                    == server_id
                )

            if status is not None:
                statement = statement.where(
                    MonitoringReportModel.status
                    == status
                )

            return int(
                session.scalar(statement) or 0
            )

    def get_with_server(
        self,
        report_id: int,
    ) -> tuple[
        MonitoringReportModel,
        ServerModel,
    ] | None:
        with self._session_factory() as session:
            statement = (
                select(
                    MonitoringReportModel,
                    ServerModel,
                )
                .join(
                    ServerModel,
                    ServerModel.id
                    == MonitoringReportModel.server_id,
                )
                .options(
                    selectinload(
                        MonitoringReportModel.executions
                    )
                )
                .where(
                    MonitoringReportModel.id
                    == report_id
                )
            )

            return session.execute(
                statement
            ).first()