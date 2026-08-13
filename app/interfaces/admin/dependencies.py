from app.runtime.claude.observability import (
    ClaudeAgentObservabilityService,
)
from app.capabilities.investigation.read_service import (
    InvestigationReadService,
)
from app.runtime.claude.supervisor import (
    ClaudeSupervisor,
)
from app.interfaces.mcp.registry import (
    ProjectMcpToolBoundary,
)
from app.capabilities.knowledge.source_service import (
    KnowledgeSourceService,
)
from app.capabilities.investigation.specialist_service import (
    SpecialistDefinitionService,
)
from app.composition import container
from app.interfaces.admin.services.ssh_test_service import (
    SSHTestService,
)
from app.interfaces.admin.services.report_pdf_service import (
    ReportPdfService,
)
from app.infrastructure.database.repositories.analysis_source_repository import (
    AnalysisSourceRepository,
)
from app.capabilities.monitoring.command_service import CommandService
from app.capabilities.monitoring.report_query_service import ReportQueryService
from app.capabilities.monitoring.server_service import ServerService
from app.capabilities.monitoring.profile_service import (
    MonitoringProfileService,
)
from app.capabilities.remediation.service import RemediationService
from app.capabilities.remediation.autonomous_policy_service import AutonomousPolicyService
from app.capabilities.remediation.autonomous_candidate_service import AutonomousCandidateService
from app.capabilities.remediation.autonomous_execution_service import AutonomousExecutionService
from app.infrastructure.database.repositories.analysis_repository import (
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

def get_specialist_definition_service(
) -> SpecialistDefinitionService:
    return container.specialist_definition_service

def get_knowledge_source_service(
) -> KnowledgeSourceService:
    return container.knowledge_source_service


def get_investigation_read_service(
) -> InvestigationReadService:
    return container.investigation_read_service


def get_claude_supervisor() -> ClaudeSupervisor:
    return container.claude_supervisor


def get_project_tool_boundary(
) -> ProjectMcpToolBoundary:
    return container.project_mcp_tool_boundary


def get_remediation_service() -> RemediationService:
    return container.remediation_service


def get_autonomous_policy_service() -> AutonomousPolicyService:
    return container.autonomous_policy_service


def get_autonomous_candidate_service() -> AutonomousCandidateService:
    return container.autonomous_candidate_service


def get_autonomous_execution_service() -> AutonomousExecutionService:
    return container.autonomous_execution_service

def get_claude_agent_observability_service(
) -> ClaudeAgentObservabilityService:
    return ClaudeAgentObservabilityService(
        container.agent_job_repository
    )
