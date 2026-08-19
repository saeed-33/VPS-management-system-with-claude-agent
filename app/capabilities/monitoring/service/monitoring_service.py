"""مكوّن دورة مراقبة السيرفر."""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from time import perf_counter

from app.capabilities.monitoring.report_service import ReportService
from asyncssh import Error
from app.infrastructure.ssh.client.client import SSHClient
from app.infrastructure.ssh.client.config import SSHConnectionConfig
from app.infrastructure.ssh.command_executor.result import CommandExecutionResult
from app.infrastructure.ssh.command_executor.executor import SSHCommandExecutor
from app.core.contracts.reports.monitoring_report_data import MonitoringReportData
from app.core.contracts.reports.monitoring_report_status import MonitoringReportStatus

from .monitoring_command_record import MonitoringCommandRecord
from .monitoring_profile_repository_protocol import MonitoringProfileRepositoryProtocol
from .report_repository_protocol import ReportRepositoryProtocol
from .server_record import ServerRecord
from .server_repository_protocol import ServerRepositoryProtocol

logger = logging.getLogger(__name__)

class MonitoringService:
    """
    خدمة تنفذ فحوص السيرفر وتجمعها في تقرير واحد وتحدث حالته.
    """

    def __init__(
        self,
        *,
        server_repository: ServerRepositoryProtocol,
        profile_repository: (
            MonitoringProfileRepositoryProtocol
        ),
        report_repository: ReportRepositoryProtocol,
        default_private_key_path: str,
        known_hosts_path: str,
        connection_timeout_seconds: float,
    ) -> None:
        """
        يجهز دورة المراقبة بمصادر السيرفر والفحوص والتقارير وإعدادات الاتصال.
        """
        self._server_repository = server_repository
        self._profile_repository = (
            profile_repository
        )
        self._report_repository = report_repository

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
        """
        ينفذ دورة الفحص لسيرفر واحد، يحفظ التقرير، ويحدث حالته بما يصف القياس الحالي فقط.
        """
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

        # يحدد الملف المختار والفحوص المفعلة ما الذي نريد معرفته عن السيرفر.

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
            # تجمع الدورة نتائج الفحوص في تقرير واحد حتى تستخدم المراحل التالية
            # صورة السيرفر نفسها بدل إعادة قراءة نتائج متفرقة.
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
            SSHError,
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

        # نحفظ التقرير أولًا حتى تشير حالة السيرفر إلى صورة موجودة يمكن تحليلها.
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
        """
        ينفذ الفحوص المفعلة بالترتيب ويعيد نتيجة كل فحص حتى لا تضيع مخرجات أو أخطاء الدورة.
        """
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
                    fingerprint_strategy=(
                        command.fingerprint_strategy
                    ),
                    fingerprint_config=(
                        command.fingerprint_config
                    ),
                )

                executions.append(result)

        return executions


    def _update_server_status(
        self,
        *,
        server_id: int,
        report: MonitoringReportData,
        report_id: int,
    ) -> None:
        """
        يحدث حالة السيرفر بعد التقرير مع إبقاء الحالة مرتبطة بآخر نتيجة مراقبة محفوظة.
        """
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
        """
        يحسب مدة دورة المراقبة بالميلي ثانية لتظهر في التقرير.
        """
        return round(
            (
                perf_counter()
                - started_counter
            ) * 1000,
            2,
        )
