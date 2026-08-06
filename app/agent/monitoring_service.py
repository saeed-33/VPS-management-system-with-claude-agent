import logging
from datetime import UTC, datetime
from time import perf_counter
from typing import TYPE_CHECKING, Protocol

import asyncssh

from app.agent.report_service import ReportService
from app.agent.ssh.client import (
    SSHClient,
    SSHConnectionConfig,
)
from app.agent.ssh.command_executor import (
    CommandExecutionResult,
    SSHCommandExecutor,
)
from app.shared.dto.reports import (
    MonitoringReportData,
    MonitoringReportStatus,
)


if TYPE_CHECKING:
    from app.agent.analysis.analysis_agent_manager import (
        AnalysisAgentManager,
    )


logger = logging.getLogger(__name__)


class ServerRecord(Protocol):
    id: int
    host: str
    port: int
    username: str

    private_key_path: str | None

    monitor_enabled: bool
    monitoring_profile_id: int | None


class MonitoringCommandRecord(Protocol):
    id: int
    name: str
    command: str
    timeout_seconds: float
    execution_order: int


class ServerRepositoryProtocol(Protocol):
    def get_by_id(
        self,
        server_id: int,
    ) -> ServerRecord | None:
        ...

    def update_monitoring_status(
        self,
        *,
        server_id: int,
        status: str,
        checked_at: datetime,
        success_at: datetime | None,
        error_message: str | None,
        report_id: int | None,
    ) -> None:
        ...


class MonitoringProfileRepositoryProtocol(
    Protocol
):
    def list_enabled_commands_for_server(
        self,
        server_id: int,
    ) -> list[MonitoringCommandRecord]:
        ...


class ReportRepositoryProtocol(Protocol):
    def create(
        self,
        report: MonitoringReportData,
    ) -> int:
        ...


class MonitoringService:
    """
    ينفذ دورة مراقبة واحدة لسيرفر واحد.

    المسؤوليات:
    - تحميل السيرفر.
    - تحميل أوامر ملف المراقبة.
    - فتح اتصال SSH.
    - تنفيذ الأوامر بالتسلسل.
    - إنشاء التقرير.
    - حفظ التقرير.
    - إرسال التقرير إلى وكيل التحليل الفرعي.
    - تحديث حالة السيرفر.

    لا يحتوي على منطق SQL مباشر.
    """

    def __init__(
        self,
        *,
        server_repository: ServerRepositoryProtocol,
        profile_repository: (
            MonitoringProfileRepositoryProtocol
        ),
        report_repository: ReportRepositoryProtocol,
        analysis_agent_manager: (
            "AnalysisAgentManager | None"
        ) = None,
        default_private_key_path: str,
        known_hosts_path: str,
        connection_timeout_seconds: float,
    ) -> None:
        self._server_repository = server_repository
        self._profile_repository = (
            profile_repository
        )
        self._report_repository = report_repository

        self._analysis_agent_manager = (
            analysis_agent_manager
        )

        self._default_private_key_path = (
            default_private_key_path
        )

        self._known_hosts_path = known_hosts_path

        self._connection_timeout_seconds = (
            connection_timeout_seconds
        )

        self._report_service = ReportService()

    async def run(
        self,
        server_id: int,
    ) -> MonitoringReportData:
        cycle_started_at = datetime.now(UTC)
        cycle_counter = perf_counter()

        server = self._server_repository.get_by_id(
            server_id
        )

        if server is None:
            raise ValueError(
                f"Server with id {server_id} "
                f"was not found."
            )

        if not server.monitor_enabled:
            raise ValueError(
                f"Monitoring is disabled for server "
                f"{server_id}."
            )

        if server.monitoring_profile_id is None:
            raise ValueError(
                f"Server {server_id} does not have "
                f"a monitoring profile."
            )

        commands = (
            self._profile_repository
            .list_enabled_commands_for_server(
                server_id
            )
        )

        if not commands:
            logger.warning(
                "Monitoring profile contains no enabled "
                "commands | server_id=%s | profile_id=%s",
                server_id,
                server.monitoring_profile_id,
            )

        private_key_path = (
            server.private_key_path
            or self._default_private_key_path
        )

        connection_config = SSHConnectionConfig(
            host=server.host,
            port=server.port,
            username=server.username,
            private_key_path=private_key_path,
            known_hosts_path=self._known_hosts_path,
            connect_timeout_seconds=(
                self._connection_timeout_seconds
            ),
        )

        try:
            executions = await self._execute_commands(
                connection_config=connection_config,
                commands=commands,
            )

            report = (
                self._report_service
                .build_successful_connection_report(
                    server_id=server_id,
                    started_at=cycle_started_at,
                    finished_at=datetime.now(UTC),
                    duration_ms=self._duration_ms(
                        cycle_counter
                    ),
                    executions=executions,
                )
            )

        except (
            asyncssh.Error,
            OSError,
            TimeoutError,
            FileNotFoundError,
        ) as exc:
            logger.warning(
                "SSH connection failed | "
                "server_id=%s | error=%s",
                server_id,
                exc,
            )

            report = (
                self._report_service
                .build_connection_failure_report(
                    server_id=server_id,
                    started_at=cycle_started_at,
                    duration_ms=self._duration_ms(
                        cycle_counter
                    ),
                    error=exc,
                )
            )

        except Exception as exc:
            logger.exception(
                "Unexpected monitoring failure | "
                "server_id=%s",
                server_id,
            )

            report = (
                self._report_service
                .build_unexpected_failure_report(
                    server_id=server_id,
                    started_at=cycle_started_at,
                    duration_ms=self._duration_ms(
                        cycle_counter
                    ),
                    error=exc,
                )
            )

        report_id = self._report_repository.create(
            report
        )

        logger.info(
            "Monitoring report saved | "
            "server_id=%s | report_id=%s | "
            "status=%s",
            server_id,
            report_id,
            report.status.value,
        )

        await self._enqueue_analysis(
            server_id=server_id,
            report_id=report_id,
        )

        self._update_server_status(
            server_id=server_id,
            report=report,
            report_id=report_id,
        )

        return report

    async def _execute_commands(
        self,
        *,
        connection_config: SSHConnectionConfig,
        commands: list[MonitoringCommandRecord],
    ) -> list[CommandExecutionResult]:
        executions: list[
            CommandExecutionResult
        ] = []

        async with SSHClient(
            connection_config
        ) as ssh_client:
            executor = SSHCommandExecutor(
                ssh_client
            )

            sorted_commands = sorted(
                commands,
                key=lambda item: (
                    item.execution_order
                ),
            )

            for command in sorted_commands:
                logger.debug(
                    "Executing monitoring command | "
                    "command_id=%s | command_name=%s | "
                    "order=%s",
                    command.id,
                    command.name,
                    command.execution_order,
                )

                result = await executor.execute(
                    command_id=command.id,
                    command_name=command.name,
                    command_text=command.command,
                    execution_order=(
                        command.execution_order
                    ),
                    timeout_seconds=(
                        command.timeout_seconds
                    ),
                )

                executions.append(result)

        return executions

    async def _enqueue_analysis(
        self,
        *,
        server_id: int,
        report_id: int,
    ) -> None:
        """
        يرسل التقرير إلى وكيل التحليل الفرعي الخاص
        بالسيرفر.

        فشل Queue أو LLM لا يؤدي إلى فشل دورة المراقبة.
        """

        if self._analysis_agent_manager is None:
            logger.debug(
                "LLM analysis disabled | "
                "server_id=%s | report_id=%s",
                server_id,
                report_id,
            )

            return

        try:
            await (
                self._analysis_agent_manager
                .enqueue_report(
                    server_id=server_id,
                    report_id=report_id,
                )
            )

        except Exception:
            logger.exception(
                "Failed to enqueue report analysis | "
                "server_id=%s | report_id=%s",
                server_id,
                report_id,
            )

    def _update_server_status(
        self,
        *,
        server_id: int,
        report: MonitoringReportData,
        report_id: int,
    ) -> None:
        now = datetime.now(UTC)

        if (
            report.status
            == MonitoringReportStatus.SUCCESS
        ):
            server_status = "online"
            success_at = now
            error_message = None

        elif (
            report.status
            == MonitoringReportStatus.PARTIAL_FAILURE
        ):
            server_status = "degraded"
            success_at = None

            error_message = (
                f"{report.commands_failed} monitoring "
                f"command(s) failed."
            )

        else:
            server_status = "offline"
            success_at = None
            error_message = report.error_message

        try:
            (
                self._server_repository
                .update_monitoring_status(
                    server_id=server_id,
                    status=server_status,
                    checked_at=now,
                    success_at=success_at,
                    error_message=error_message,
                    report_id=report_id,
                )
            )

        except Exception:
            logger.exception(
                "Failed to update server monitoring "
                "status | server_id=%s | report_id=%s",
                server_id,
                report_id,
            )

    @staticmethod
    def _duration_ms(
        started_counter: float,
    ) -> float:
        return round(
            (
                perf_counter()
                - started_counter
            ) * 1000,
            2,
        )