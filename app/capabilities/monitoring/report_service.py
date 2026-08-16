"""
تجميع نتائج دورة المراقبة في تقرير يصف الاتصال والفحوص دون تشخيص السبب.
"""
from datetime import UTC, datetime

from app.infrastructure.ssh.command_executor import (
    CommandExecutionResult,
)
from app.core.contracts.reports import (
    CommandExecutionData,
    MonitoringReportData,
    MonitoringReportStatus,
)


class ReportService:
    """
    خدمة تبني حالات التقرير المختلفة من نتائج الاتصال والفحوص.
    """
    def build_successful_connection_report(
        self,
        *,
        server_id: int,
        started_at: datetime,
        finished_at: datetime,
        duration_ms: float,
        executions: list[CommandExecutionResult],
    ) -> MonitoringReportData:
        """
        يبني تقريرًا من اتصال ناجح ونتائج الفحوص التي نفذت.
        """
        execution_data = [
            CommandExecutionData(
                command_id=item.command_id,
                command_name=item.command_name,
                command_text=item.command_text,
                execution_order=item.execution_order,
                success=item.success,
                exit_status=item.exit_status,
                stdout=item.stdout,
                stderr=item.stderr,
                error_message=item.error_message,
                started_at=item.started_at,
                finished_at=item.finished_at,
                duration_ms=item.duration_ms,
                fingerprint_strategy=(
                    item.fingerprint_strategy
                ),
                fingerprint_config=(
                    item.fingerprint_config
                ),
            )
            for item in executions
        ]

        commands_total = len(execution_data)

        commands_succeeded = sum(
            1
            for execution in execution_data
            if execution.success
        )

        commands_failed = (
            commands_total - commands_succeeded
        )

        status = (
            MonitoringReportStatus.SUCCESS
            if commands_failed == 0
            else MonitoringReportStatus.PARTIAL_FAILURE
        )

        return MonitoringReportData(
            server_id=server_id,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            connection_successful=True,
            error_message=None,
            commands_total=commands_total,
            commands_succeeded=commands_succeeded,
            commands_failed=commands_failed,
            executions=execution_data,
        )

    def build_connection_failure_report(
        self,
        *,
        server_id: int,
        started_at: datetime,
        duration_ms: float,
        error: Exception,
    ) -> MonitoringReportData:
        """
        يبني تقريرًا يثبت فشل الاتصال قبل تنفيذ الفحوص على السيرفر.
        """
        return MonitoringReportData(
            server_id=server_id,
            status=(
                MonitoringReportStatus.CONNECTION_FAILED
            ),
            started_at=started_at,
            finished_at=datetime.now(UTC),
            duration_ms=duration_ms,
            connection_successful=False,
            error_message=(
                f"{type(error).__name__}: {error}"
            ),
            commands_total=0,
            commands_succeeded=0,
            commands_failed=0,
            executions=[],
        )

    def build_unexpected_failure_report(
        self,
        *,
        server_id: int,
        started_at: datetime,
        duration_ms: float,
        error: Exception,
    ) -> MonitoringReportData:
        """
        يبني تقرير فشل مضبوطًا عندما تتوقف الدورة بسبب خطأ غير متوقع.
        """
        return MonitoringReportData(
            server_id=server_id,
            status=MonitoringReportStatus.FAILED,
            started_at=started_at,
            finished_at=datetime.now(UTC),
            duration_ms=duration_ms,
            connection_successful=False,
            error_message=(
                f"{type(error).__name__}: {error}"
            ),
            commands_total=0,
            commands_succeeded=0,
            commands_failed=0,
            executions=[],
        )
