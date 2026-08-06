from app.bootstrap import container
from app.admin.services.ssh_test_service import (
    SSHTestService,
)
from app.admin.services.report_pdf_service import (
    ReportPdfService,
)
from app.shared.database.repositories.analysis_source_repository import (
    AnalysisSourceRepository,
)
from app.shared.services import (
    CommandService,
    ReportQueryService,
    ServerService,
)
from app.shared.services.profile_service import (
    MonitoringProfileService,
)
from app.shared.database.repositories.analysis_repository import (
    AnalysisRepository,
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


def get_analysis_repository() -> AnalysisRepository:
    return container.analysis_repository


def get_analysis_source_repository(
) -> AnalysisSourceRepository:
    return container.analysis_source_repository


def get_report_pdf_service() -> ReportPdfService:
    service = container.report_pdf_service

    if service is None:
        raise RuntimeError(
            "PDF export service is not configured."
        )

    return service
