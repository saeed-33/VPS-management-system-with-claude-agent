"""
جزء من Monitoring لاختيار profile/commands أو تنفيذ الدورة وحفظ report.

الموقع في المعمارية: Application capability / monitoring.
يُستدعى بواسطة: Scheduler أو MCP أو Admin API.
يعتمد مباشرة على: app.infrastructure.ssh.command_executor، app.core.contracts.reports.
الحد المعماري: لا يقوم بتحليل LLM أو Investigation.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    يمثل ReportService مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        يبني DTO أو dependency graph من المدخلات ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى build_successful_connection_report؛ المدخلات المهمة: server_id، started_at، finished_at، duration_ms، executions.
        تعيد MonitoringReportData أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يبني DTO أو dependency graph من المدخلات ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى build_connection_failure_report؛ المدخلات المهمة: server_id، started_at، duration_ms، error.
        تعيد MonitoringReportData أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يبني DTO أو dependency graph من المدخلات ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى build_unexpected_failure_report؛ المدخلات المهمة: server_id، started_at، duration_ms، error.
        تعيد MonitoringReportData أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
