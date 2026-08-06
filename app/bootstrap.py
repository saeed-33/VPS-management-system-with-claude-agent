from dataclasses import dataclass

from app.admin.services.ssh_test_service import (
    SSHTestService,
)
from app.agent.analysis.analysis_agent_manager import (
    AnalysisAgentManager,
)
from app.agent.analysis.client_factory import (
    create_llm_analysis_client,
)
from app.agent.analysis.report_analyzer import (
    ReportAnalyzer,
)
from app.agent.monitoring_service import (
    MonitoringService,
)
from app.agent.scheduler import MonitoringScheduler
from app.shared.config import settings
from app.shared.database.repositories.analysis_repository import (
    AnalysisRepository,
)
from app.shared.database.repositories.command_repository import (
    CommandRepository,
)
from app.shared.database.repositories.profile_repository import (
    MonitoringProfileRepository,
)
from app.shared.database.repositories.report_repository import (
    ReportRepository,
)
from app.shared.database.repositories.server_repository import (
    ServerRepository,
)
from app.shared.services.command_service import (
    CommandService,
)
from app.shared.services.profile_service import (
    MonitoringProfileService,
)
from app.shared.services.report_service import (
    ReportQueryService,
)
from app.shared.services.server_service import (
    ServerService,
)


@dataclass(slots=True)
class ApplicationContainer:
    # Repositories
    server_repository: ServerRepository
    command_repository: CommandRepository
    profile_repository: MonitoringProfileRepository
    report_repository: ReportRepository
    analysis_repository: AnalysisRepository

    # Shared services
    server_service: ServerService
    command_service: CommandService
    monitoring_profile_service: MonitoringProfileService
    report_query_service: ReportQueryService

    # Admin services
    ssh_test_service: SSHTestService

    # Monitoring agent
    monitoring_service: MonitoringService
    scheduler: MonitoringScheduler

    # LLM analysis
    report_analyzer: ReportAnalyzer | None
    analysis_agent_manager: AnalysisAgentManager | None


def build_container() -> ApplicationContainer:
    """
    يبني جميع اعتماديات التطبيق في مكان واحد.

    لا يجب إنشاء Repositories أو Services داخل Routes
    أو داخل الوكيل مباشرة.
    """

    # -------------------------------------------------
    # Repositories
    # -------------------------------------------------

    server_repository = ServerRepository()
    command_repository = CommandRepository()
    profile_repository = MonitoringProfileRepository()
    report_repository = ReportRepository()
    analysis_repository = AnalysisRepository()

    # -------------------------------------------------
    # Shared services
    # -------------------------------------------------

    server_service = ServerService(
        repository=server_repository,
    )

    command_service = CommandService(
        command_repository=command_repository,
        server_repository=server_repository,
    )

    monitoring_profile_service = (
        MonitoringProfileService(
            profile_repository=profile_repository,
            command_repository=command_repository,
            server_repository=server_repository,
        )
    )

    report_query_service = ReportQueryService(
        repository=report_repository,
    )

    # -------------------------------------------------
    # Admin services
    # -------------------------------------------------

    ssh_test_service = SSHTestService(
        server_repository=server_repository,
        default_private_key_path=str(
            settings.default_ssh_private_key_path
        ),
        known_hosts_path=str(
            settings.ssh_known_hosts_path
        ),
        connect_timeout_seconds=(
            settings.ssh_connect_timeout_seconds
        ),
        command_timeout_seconds=(
            settings.command_timeout_seconds
        ),
    )

    # -------------------------------------------------
    # LLM analysis
    # -------------------------------------------------

    report_analyzer: ReportAnalyzer | None = None

    analysis_agent_manager: (
        AnalysisAgentManager | None
    ) = None

    if settings.llm_enabled:
        llm_client = create_llm_analysis_client(
            settings
        )

        report_analyzer = ReportAnalyzer(
            report_query_service=report_query_service,
            analysis_repository=analysis_repository,
            llm_client=llm_client,
            max_report_characters=(
                settings.llm_max_report_characters
            ),
        )

        analysis_agent_manager = (
            AnalysisAgentManager(
                report_analyzer=report_analyzer,
                analysis_repository=(
                    analysis_repository
                ),
                queue_size_per_server=(
                    settings
                    .llm_analysis_queue_size_per_server
                ),
            )
        )

    # -------------------------------------------------
    # Monitoring agent
    # -------------------------------------------------

    monitoring_service = MonitoringService(
        server_repository=server_repository,
        profile_repository=profile_repository,
        report_repository=report_repository,
        analysis_agent_manager=(
            analysis_agent_manager
        ),
        default_private_key_path=str(
            settings.default_ssh_private_key_path
        ),
        known_hosts_path=str(
            settings.ssh_known_hosts_path
        ),
        connection_timeout_seconds=(
            settings.ssh_connect_timeout_seconds
        ),
    )

    scheduler = MonitoringScheduler(
        server_repository=server_repository,
        monitoring_service=monitoring_service,
        polling_interval_seconds=(
            settings.monitor_polling_interval_seconds
        ),
        max_concurrent_servers=(
            settings.max_concurrent_servers
        ),
    )

    return ApplicationContainer(
        server_repository=server_repository,
        command_repository=command_repository,
        profile_repository=profile_repository,
        report_repository=report_repository,
        analysis_repository=analysis_repository,
        server_service=server_service,
        command_service=command_service,
        monitoring_profile_service=(
            monitoring_profile_service
        ),
        report_query_service=report_query_service,
        ssh_test_service=ssh_test_service,
        monitoring_service=monitoring_service,
        scheduler=scheduler,
        report_analyzer=report_analyzer,
        analysis_agent_manager=(
            analysis_agent_manager
        ),
    )


container = build_container()