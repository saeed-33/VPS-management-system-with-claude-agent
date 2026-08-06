from app.bootstrap import container
from app.admin.services.ssh_test_service import (
    SSHTestService,
)
from app.shared.services import (
    CommandService,
    ReportQueryService,
    ServerService,
)
from app.shared.services.profile_service import (
    MonitoringProfileService,
)


def get_monitoring_profile_service(
) -> MonitoringProfileService:
    return container.monitoring_profile_service

def get_server_service() -> ServerService:
    return container.server_service


def get_command_service() -> CommandService:
    return container.command_service


def get_report_query_service() -> ReportQueryService:
    return container.report_query_service


def get_ssh_test_service() -> SSHTestService:
    return container.ssh_test_service