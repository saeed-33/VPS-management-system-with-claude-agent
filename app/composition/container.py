"""
يركب dependencies ويربط repositories والخدمات والـruntime.

الموقع في المعمارية: Bootstrap / dependency composition.
يُستدعى بواسطة: app.main أو الاختبارات عند إنشاء container.
يعتمد مباشرة على: app.interfaces.admin.services.report_pdf_service، app.interfaces.admin.services.ssh_test_service، app.capabilities.remediation.autonomous_policy_service، app.capabilities.remediation.autonomous_history_service، app.capabilities.remediation.autonomous_candidate_service، app.capabilities.remediation.autonomous_authorization_service.
الحد المعماري: لا ينفذ workflow business؛ دوره wiring وترتيب الإنشاء.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.interfaces.admin.services.report_pdf_service import ReportPdfService
from app.interfaces.admin.services.ssh_test_service import SSHTestService
from app.capabilities.remediation.autonomous_policy_service import AutonomousPolicyService
from app.capabilities.remediation.autonomous_history_service import AutonomousHistoryService
from app.capabilities.remediation.autonomous_candidate_service import AutonomousCandidateService
from app.capabilities.remediation.autonomous_authorization_service import AutonomousAuthorizationService
from app.capabilities.remediation.autonomous_execution_service import AutonomousExecutionService
from app.capabilities.analysis.analysis_orchestrator import AnalysisOrchestrator
from app.capabilities.analysis.report_analyzer import ReportAnalyzer
from app.core.policies.diagnostic_policy import DiagnosticPolicyEngine
from app.core.policies.diagnostic_tools import DiagnosticToolRegistry
from app.capabilities.investigation.evidence_collection import EvidenceCollectionService
from app.capabilities.investigation.investigation_router import InvestigationRouter
from app.capabilities.investigation.persistence_service import InvestigationPersistenceService
from app.capabilities.investigation.runtime_snapshot_service import InvestigationRuntimeSnapshotService
from app.capabilities.investigation.specialist_execution_service import SpecialistExecutionService
from app.capabilities.investigation.specialist_investigation_loop import SpecialistInvestigationLoop
from app.capabilities.investigation.specialist_registry import SpecialistRegistry
from app.capabilities.knowledge.chunking_service import KnowledgeChunkingService
from app.capabilities.knowledge.ingestion_service import KnowledgeIngestionService
from app.capabilities.knowledge.source_registry import KnowledgeSourceRegistry
from app.runtime.claude.job_service import ClaudeAgentJobService
from app.runtime.claude.supervisor import ClaudeSupervisor
from app.infrastructure.database.repositories.agent_job_repository import AgentJobRepository
from app.infrastructure.database.repositories.analysis_repository import AnalysisRepository
from app.infrastructure.database.repositories.analysis_source_repository import AnalysisSourceRepository
from app.infrastructure.database.repositories.command_repository import CommandRepository
from app.infrastructure.database.repositories.investigation_repository import InvestigationRepository
from app.infrastructure.database.repositories.knowledge_document_repository import KnowledgeDocumentRepository
from app.infrastructure.database.repositories.knowledge_source_repository import KnowledgeSourceRepository
from app.infrastructure.database.repositories.profile_repository import MonitoringProfileRepository
from app.infrastructure.database.repositories.remediation_repository import RemediationRepository
from app.infrastructure.database.repositories.report_repository import ReportRepository
from app.infrastructure.database.repositories.server_repository import ServerRepository
from app.infrastructure.database.repositories.specialist_definition_repository import SpecialistDefinitionRepository
from app.capabilities.monitoring.command_service import CommandService
from app.capabilities.investigation.read_service import InvestigationReadService
from app.capabilities.knowledge.source_service import KnowledgeSourceService
from app.capabilities.monitoring.profile_service import MonitoringProfileService
from app.capabilities.remediation.service import RemediationService
from app.capabilities.remediation.issue_fingerprint_service import IssueFingerprintService
from app.capabilities.monitoring.report_query_service import ReportQueryService
from app.capabilities.monitoring.server_service import ServerService
from app.capabilities.investigation.specialist_service import SpecialistDefinitionService
from app.capabilities.monitoring.scheduler import MonitoringScheduler
from app.capabilities.monitoring.service import MonitoringService
from app.interfaces.mcp.registry import ProjectMcpToolBoundary


@dataclass(slots=True)
class ApplicationContainer:
    """
    يمثل ApplicationContainer مسؤولية محددة داخل طبقة Bootstrap / dependency composition.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه app.main أو الاختبارات عند إنشاء container
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    server_repository: ServerRepository
    command_repository: CommandRepository
    profile_repository: MonitoringProfileRepository
    report_repository: ReportRepository
    analysis_repository: AnalysisRepository
    analysis_source_repository: AnalysisSourceRepository
    specialist_definition_repository: SpecialistDefinitionRepository
    investigation_repository: InvestigationRepository
    knowledge_source_repository: KnowledgeSourceRepository
    knowledge_document_repository: KnowledgeDocumentRepository
    agent_job_repository: AgentJobRepository
    remediation_repository: RemediationRepository
    autonomous_remediation_repository: object

    server_service: ServerService
    command_service: CommandService
    monitoring_profile_service: MonitoringProfileService
    report_query_service: ReportQueryService
    specialist_definition_service: SpecialistDefinitionService
    specialist_registry: SpecialistRegistry
    investigation_router: InvestigationRouter
    investigation_persistence_service: InvestigationPersistenceService
    investigation_read_service: InvestigationReadService
    investigation_runtime_snapshot_service: InvestigationRuntimeSnapshotService
    specialist_execution_service: SpecialistExecutionService
    knowledge_source_service: KnowledgeSourceService
    knowledge_source_registry: KnowledgeSourceRegistry
    knowledge_ingestion_service: KnowledgeIngestionService
    knowledge_chunking_service: KnowledgeChunkingService
    diagnostic_tool_registry: DiagnosticToolRegistry
    diagnostic_policy_engine: DiagnosticPolicyEngine
    evidence_collection_service: EvidenceCollectionService
    remediation_service: RemediationService
    issue_fingerprint_service: IssueFingerprintService
    autonomous_policy_service: AutonomousPolicyService
    autonomous_history_service: AutonomousHistoryService
    autonomous_candidate_service: AutonomousCandidateService
    autonomous_authorization_service: AutonomousAuthorizationService
    autonomous_execution_service: AutonomousExecutionService
    specialist_investigation_loop: SpecialistInvestigationLoop | None
    claude_agent_job_service: ClaudeAgentJobService
    project_mcp_tool_boundary: ProjectMcpToolBoundary
    claude_supervisor: ClaudeSupervisor

    ssh_test_service: SSHTestService

    monitoring_service: MonitoringService
    scheduler: MonitoringScheduler

    report_analyzer: ReportAnalyzer | None
    analysis_orchestrator: AnalysisOrchestrator | None
    report_pdf_service: ReportPdfService | None


__all__ = [
    "ApplicationContainer",
]
