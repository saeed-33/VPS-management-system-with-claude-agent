"""
قراءة تقارير المراقبة وعرض ملخصاتها وتفاصيل قياساتها.
"""
from app.core.ports.monitoring.report_repository import ReportRepositoryPort
from app.core.contracts.reports.command_execution_dto import CommandExecutionDTO
from app.core.contracts.reports.report_details_dto import ReportDetailsDTO
from app.core.contracts.reports.report_list_item_dto import ReportListItemDTO
from app.core.exceptions.report_not_found_error import ReportNotFoundError


class ReportQueryService:
    """
    خدمة تعرض تقارير المراقبة بقائمة مختصرة أو تفاصيل كاملة.
    """
    def __init__(
        self,
        repository: ReportRepositoryPort,
    ) -> None:
        """
        يدير دورة حياة عنصر تقارير المراقبة داخل الخدمة.
        """
        self._repository = repository

    def list_reports(
        self,
        *,
        server_id: int | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[
        list[ReportListItemDTO],
        int,
    ]:
        """
        يعرض تقارير المراقبة في قائمة مختصرة قابلة للتصفية والترقيم.
        """
        if page < 1:
            raise ValueError(
                "Page must be greater than zero."
            )

        if not 1 <= page_size <= 200:
            raise ValueError(
                "Page size must be between "
                "1 and 200."
            )

        offset = (page - 1) * page_size

        rows = self._repository.list_reports(
            server_id=server_id,
            status=status,
            offset=offset,
            limit=page_size,
        )

        total = self._repository.count_reports(
            server_id=server_id,
            status=status,
        )

        items = [
            ReportListItemDTO(
                id=report.id,
                server_id=server.id,
                server_name=server.name,
                status=report.status,
                started_at=report.started_at,
                finished_at=report.finished_at,
                duration_ms=report.duration_ms,
                connection_successful=(
                    report.connection_successful
                ),
                commands_total=(
                    report.commands_total
                ),
                commands_succeeded=(
                    report.commands_succeeded
                ),
                commands_failed=(
                    report.commands_failed
                ),
            )
            for report, server in rows
        ]

        return items, total

    def get_report(
        self,
        report_id: int,
    ) -> ReportDetailsDTO:
        """
        يسترجع تقريرًا كاملًا مع نتائج فحوصه لاستخدامه في التحليل أو العرض.
        """
        row = self._repository.get_with_server(
            report_id
        )

        if row is None:
            raise ReportNotFoundError(report_id)

        report, server = row

        executions = [
            CommandExecutionDTO(
                id=execution.id,
                command_id=execution.command_id,
                command_name=(
                    execution.command_name
                ),
                command_text=(
                    execution.command_text
                ),
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
                started_at=execution.started_at,
                finished_at=execution.finished_at,
                duration_ms=execution.duration_ms,
                fingerprint_strategy=(
                    execution.fingerprint_strategy
                ),
                fingerprint_config=(
                    execution.fingerprint_config
                ),
            )
            for execution in report.executions
        ]

        return ReportDetailsDTO(
            id=report.id,
            server_id=server.id,
            monitoring_profile_id=(
                server.monitoring_profile_id
            ),
            server_name=server.name,
            server_host=server.host,
            status=report.status,
            started_at=report.started_at,
            finished_at=report.finished_at,
            duration_ms=report.duration_ms,
            connection_successful=(
                report.connection_successful
            ),
            error_message=report.error_message,
            commands_total=report.commands_total,
            commands_succeeded=(
                report.commands_succeeded
            ),
            commands_failed=(
                report.commands_failed
            ),
            executions=executions,
        )
