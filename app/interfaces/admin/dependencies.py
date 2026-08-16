"""
جزء من واجهة الإدارة يعرّف route أو payload أو عرضًا للمشغل.

الموقع في المعمارية: Administration interface.
يُستدعى بواسطة: FastAPI أو متصفح الإدارة.
يعتمد مباشرة على: app.runtime.claude.observability، app.capabilities.investigation.read_service، app.runtime.claude.supervisor، app.interfaces.mcp.registry، app.capabilities.knowledge.source_service، app.capabilities.investigation.specialist_service.
الحد المعماري: العرض والتحقق الشكلي لا يمنحان صلاحية تنفيذ؛ authorization في الخدمة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from fastapi import Request

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
from app.interfaces.admin.auth import (
    AdminAuthService,
    AdminPrincipal,
    get_admin_principal,
)


def get_monitoring_profile_service(
) -> MonitoringProfileService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_monitoring_profile_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد MonitoringProfileService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.monitoring_profile_service

def get_server_service() -> ServerService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_server_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد ServerService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.server_service


def get_command_service() -> CommandService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_command_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد CommandService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.command_service


def get_report_query_service() -> ReportQueryService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_report_query_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد ReportQueryService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.report_query_service


def get_ssh_test_service() -> SSHTestService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_ssh_test_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد SSHTestService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.ssh_test_service


def get_analysis_repository() -> AnalysisRepository:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_analysis_repository؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد AnalysisRepository أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.analysis_repository


def get_analysis_source_repository(
) -> AnalysisSourceRepository:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_analysis_source_repository؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد AnalysisSourceRepository أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.analysis_source_repository


def get_report_pdf_service() -> ReportPdfService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_report_pdf_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد ReportPdfService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_specialist_definition_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد SpecialistDefinitionService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.specialist_definition_service

def get_knowledge_source_service(
) -> KnowledgeSourceService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_knowledge_source_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد KnowledgeSourceService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.knowledge_source_service


def get_investigation_read_service(
) -> InvestigationReadService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_investigation_read_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد InvestigationReadService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.investigation_read_service


def get_claude_supervisor() -> ClaudeSupervisor:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_claude_supervisor؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد ClaudeSupervisor أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.claude_supervisor


def get_project_tool_boundary(
) -> ProjectMcpToolBoundary:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_project_tool_boundary؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد ProjectMcpToolBoundary أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.project_mcp_tool_boundary


def get_remediation_service() -> RemediationService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_remediation_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد RemediationService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.remediation_service


def get_autonomous_policy_service() -> AutonomousPolicyService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_autonomous_policy_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد AutonomousPolicyService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.autonomous_policy_service


def get_autonomous_candidate_service() -> AutonomousCandidateService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_autonomous_candidate_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد AutonomousCandidateService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.autonomous_candidate_service


def get_autonomous_execution_service() -> AutonomousExecutionService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_autonomous_execution_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد AutonomousExecutionService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return container.autonomous_execution_service


def get_admin_auth_service(request: Request) -> AdminAuthService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_admin_auth_service؛ المدخلات المهمة: request.
    تعيد AdminAuthService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return request.app.state.admin_auth_service


def get_current_admin(request: Request) -> AdminPrincipal:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_current_admin؛ المدخلات المهمة: request.
    تعيد AdminPrincipal أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return get_admin_principal(request)

def get_claude_agent_observability_service(
) -> ClaudeAgentObservabilityService:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى get_claude_agent_observability_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد ClaudeAgentObservabilityService أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return ClaudeAgentObservabilityService(
        container.agent_job_repository
    )
