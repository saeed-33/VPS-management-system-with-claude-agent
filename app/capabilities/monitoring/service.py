"""
جزء من Monitoring لاختيار profile/commands أو تنفيذ الدورة وحفظ report.

الموقع في المعمارية: Application capability / monitoring.
يُستدعى بواسطة: Scheduler أو MCP أو Admin API.
يعتمد مباشرة على: app.capabilities.monitoring.report_service، app.infrastructure.ssh، app.infrastructure.ssh.client، app.infrastructure.ssh.command_executor، app.core.contracts.reports.
الحد المعماري: لا يقوم بتحليل LLM أو Investigation.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
import logging
from datetime import UTC, datetime
from time import perf_counter
from typing import Protocol

from app.capabilities.monitoring.report_service import ReportService
from app.infrastructure.ssh import SSHError
from app.infrastructure.ssh.client import (
    SSHClient,
    SSHConnectionConfig,
)
from app.infrastructure.ssh.command_executor import (
    CommandExecutionResult,
    SSHCommandExecutor,
)
from app.core.contracts.reports import (
    MonitoringReportData,
    MonitoringReportStatus,
)


logger = logging.getLogger(__name__)


class ServerRecord(Protocol):
    """
    يمثل ServerRecord مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    id: int
    host: str
    port: int
    username: str

    private_key_path: str | None

    monitor_enabled: bool
    monitoring_profile_id: int | None


class MonitoringCommandRecord(Protocol):
    """
    يمثل MonitoringCommandRecord مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    id: int
    name: str
    command: str
    timeout_seconds: float
    execution_order: int


class ServerRepositoryProtocol(Protocol):
    """
    يمثل ServerRepositoryProtocol مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def get_by_id(
        self,
        server_id: int,
    ) -> ServerRecord | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى get_by_id؛ المدخلات المهمة: server_id.
        تعيد ServerRecord | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى update_monitoring_status؛ المدخلات المهمة: server_id، status، checked_at، success_at، error_message، report_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        ...


class MonitoringProfileRepositoryProtocol(
    Protocol
):
    """
    يمثل MonitoringProfileRepositoryProtocol مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def list_enabled_commands_for_server(
        self,
        server_id: int,
    ) -> list[MonitoringCommandRecord]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى list_enabled_commands_for_server؛ المدخلات المهمة: server_id.
        تعيد list[MonitoringCommandRecord] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        ...


class ReportRepositoryProtocol(Protocol):
    """
    يمثل ReportRepositoryProtocol مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def create(
        self,
        report: MonitoringReportData,
    ) -> int:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى create؛ المدخلات المهمة: report.
        تعيد int أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        default_private_key_path: str,
        known_hosts_path: str,
        connection_timeout_seconds: float,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: server_repository، profile_repository، report_repository، default_private_key_path، known_hosts_path، connection_timeout_seconds.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يشغّل workflow هذه الطبقة ويربط مراحله ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى run؛ المدخلات المهمة: server_id.
        تعيد MonitoringReportData أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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

        # profile/commands تحدد ما الذي يجب قياسه؛ نبقي اختيار القياسات
        # منفصلًا عن تنفيذ SSH حتى تبقى Monitoring قابلة للاختبار.

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
            # تتحول نتائج SSH الخام إلى report موحد قبل الحفظ، ليصبح report_id
            # رابطًا قابلًا للتتبع لمراحل Analysis وواجهات القراءة اللاحقة.
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

        # نحفظ التقرير قبل تحديث حالة السيرفر حتى تشير الحالة إلى report موجود.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى _execute_commands؛ المدخلات المهمة: connection_config، commands.
        تعيد list[CommandExecutionResult] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى _update_server_status؛ المدخلات المهمة: server_id، report، report_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى _duration_ms؛ المدخلات المهمة: started_counter.
        تعيد float أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return round(
            (
                perf_counter()
                - started_counter
            ) * 1000,
            2,
        )
