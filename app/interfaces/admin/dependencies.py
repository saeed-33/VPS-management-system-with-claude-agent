"""
مصانع اعتماديات واجهة الإدارة.

تعيد هذه الدوال الخدمات والمستودعات من حاوية التطبيق، وتوفر اعتماديات FastAPI
للهوية الحالية والخدمات الإدارية دون إنشاء نسخ مستقلة لكل طلب.
"""
from fastapi import Request

from app.runtime.claude.observability.observability import ClaudeAgentObservabilityService
from app.capabilities.investigation.read_service import (
    InvestigationReadService,
)
from app.runtime.claude.supervisor.supervisor import ClaudeSupervisor
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
from app.interfaces.admin.services.ssh_test_service.service import SSHTestService
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
from app.capabilities.remediation.service.remediation_service import RemediationService
from app.capabilities.remediation.autonomous_policy_service import AutonomousPolicyService
from app.capabilities.remediation.autonomous_candidate_service import AutonomousCandidateService
from app.capabilities.remediation.autonomous_execution_service.autonomous_execution_service import AutonomousExecutionService
from app.infrastructure.database.repositories.analysis_repository.repository import AnalysisRepository
from app.interfaces.admin.auth.service import AdminAuthService
from app.interfaces.admin.auth.principal import AdminPrincipal
from app.interfaces.admin.auth.middleware import get_admin_principal


def get_monitoring_profile_service(
) -> MonitoringProfileService:
    """
    يعيد خدمة ملفات المراقبة من حاوية التطبيق.
    """
    return container.monitoring_profile_service

def get_server_service() -> ServerService:
    """
    يعيد خدمة إدارة السيرفرات من الحاوية.
    """
    return container.server_service


def get_command_service() -> CommandService:
    """
    يعيد خدمة أوامر المراقبة من الحاوية.
    """
    return container.command_service


def get_report_query_service() -> ReportQueryService:
    """
    يعيد خدمة الاستعلام عن تقارير المراقبة.
    """
    return container.report_query_service


def get_ssh_test_service() -> SSHTestService:
    """
    يعيد خدمة اختبار اتصال SSH.
    """
    return container.ssh_test_service


def get_analysis_repository() -> AnalysisRepository:
    """
    يعيد مستودع التحليلات المرتبط بقاعدة البيانات.
    """
    return container.analysis_repository


def get_analysis_source_repository(
) -> AnalysisSourceRepository:
    """
    يعيد مستودع مصادر التحليل والتدقيق.
    """
    return container.analysis_source_repository


def get_report_pdf_service() -> ReportPdfService:
    """
    يعيد خدمة توليد تقارير PDF الإدارية.
    """
    service = container.report_pdf_service

    if service is None:
        raise RuntimeError(
            "PDF export service is not configured."
        )

    return service

def get_specialist_definition_service(
) -> SpecialistDefinitionService:
    """
    يعيد خدمة تعريفات الاختصاصيين.
    """
    return container.specialist_definition_service

def get_knowledge_source_service(
) -> KnowledgeSourceService:
    """
    يعيد خدمة مصادر المعرفة.
    """
    return container.knowledge_source_service


def get_investigation_read_service(
) -> InvestigationReadService:
    """
    يعيد خدمة قراءة التحقيقات ونتائجها.
    """
    return container.investigation_read_service


def get_claude_supervisor() -> ClaudeSupervisor:
    """
    يعيد مشرف تشغيل Claude من الحاوية.
    """
    return container.claude_supervisor


def get_project_tool_boundary(
) -> ProjectMcpToolBoundary:
    """
    يعيد حد أدوات MCP المسموح لمشروع التطبيق.
    """
    return container.project_mcp_tool_boundary


def get_remediation_service() -> RemediationService:
    """
    يعيد خدمة خطط المعالجة والتنفيذ والتراجع.
    """
    return container.remediation_service


def get_autonomous_policy_service() -> AutonomousPolicyService:
    """
    يعيد خدمة سياسات المعالجة الآلية.
    """
    return container.autonomous_policy_service


def get_autonomous_candidate_service() -> AutonomousCandidateService:
    """
    يعيد خدمة مرشحي المعالجة الآلية.
    """
    return container.autonomous_candidate_service


def get_autonomous_execution_service() -> AutonomousExecutionService:
    """
    يعيد خدمة تقييم وتنفيذ القرارات الآلية.
    """
    return container.autonomous_execution_service


def get_admin_auth_service(request: Request) -> AdminAuthService:
    """
    يعيد خدمة مصادقة الإدارة والجلسات.
    """
    return request.app.state.admin_auth_service


def get_current_admin(request: Request) -> AdminPrincipal:
    """
    يعيد اعتماد FastAPI الذي يحمّل الهوية الإدارية الحالية.
    """
    return get_admin_principal(request)

def get_claude_agent_observability_service(
) -> ClaudeAgentObservabilityService:
    """
    يعيد خدمة مراقبة تنفيذ وكيل Claude.
    """
    return ClaudeAgentObservabilityService(
        container.agent_job_repository
    )
