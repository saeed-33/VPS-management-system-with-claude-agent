"""
تعريف حاوية اعتماديات التطبيق.

تحمل الحاوية الحزم المشتركة لمكونات المراقبة والتحليل والتحقيق والمعالجة
والتشغيل، لتُمرر صراحة إلى الطبقات المستهلكة.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.interfaces.admin.services.report_pdf_service import ReportPdfService
from app.core.ports.analysis.embedding_client import EmbeddingClient
from app.interfaces.admin.services.ssh_test_service.service import SSHTestService
from app.capabilities.remediation.autonomous_policy_service import AutonomousPolicyService
from app.capabilities.remediation.autonomous_history_service import AutonomousHistoryService
from app.capabilities.remediation.autonomous_candidate_service import AutonomousCandidateService
from app.capabilities.remediation.autonomous_authorization_service import AutonomousAuthorizationService
from app.capabilities.remediation.autonomous_execution_service.autonomous_execution_service import AutonomousExecutionService
from app.capabilities.analysis.analysis_orchestrator.orchestrator import AnalysisOrchestrator
from app.capabilities.analysis.report_analyzer import ReportAnalyzer
from app.core.policies.diagnostic_policy.diagnostic_policy_engine import DiagnosticPolicyEngine
from app.core.policies.diagnostic_tools.diagnostic_tool_registry import DiagnosticToolRegistry
from app.capabilities.investigation.evidence_collection.evidence_collection_service import EvidenceCollectionService
from app.capabilities.investigation.investigation_router.investigation_router import InvestigationRouter
from app.capabilities.investigation.persistence_service import InvestigationPersistenceService
from app.capabilities.investigation.runtime_snapshot_service.runtime_snapshot_service import InvestigationRuntimeSnapshotService
from app.capabilities.investigation.specialist_execution_service.specialist_execution_service import SpecialistExecutionService
from app.capabilities.investigation.specialist_investigation_loop.specialist_investigation_loop import SpecialistInvestigationLoop
from app.capabilities.investigation.backlog_worker import InvestigationBacklogWorker
from app.capabilities.investigation.specialist_registry.specialist_registry import SpecialistRegistry
from app.capabilities.knowledge.chunking_service import KnowledgeChunkingService
from app.capabilities.knowledge.ingestion_service import KnowledgeIngestionService
from app.capabilities.knowledge.source_registry.registry import KnowledgeSourceRegistry
from app.runtime.claude.job_service import ClaudeAgentJobService
from app.runtime.claude.supervisor.supervisor import ClaudeSupervisor
from app.infrastructure.database.repositories.agent_job_repository import AgentJobRepository
from app.infrastructure.database.repositories.analysis_repository.repository import AnalysisRepository
from app.infrastructure.database.repositories.analysis_source_repository import AnalysisSourceRepository
from app.infrastructure.database.repositories.command_repository.repository import CommandRepository
from app.infrastructure.database.repositories.investigation_repository.repository import InvestigationRepository
from app.infrastructure.database.repositories.knowledge_document_repository import KnowledgeDocumentRepository
from app.infrastructure.database.repositories.knowledge_source_repository import KnowledgeSourceRepository
from app.infrastructure.database.repositories.profile_repository.repository import MonitoringProfileRepository
from app.infrastructure.database.repositories.remediation_repository.repository import RemediationRepository
from app.infrastructure.database.repositories.report_repository import ReportRepository
from app.infrastructure.database.repositories.server_repository import ServerRepository
from app.infrastructure.database.repositories.specialist_definition_repository import SpecialistDefinitionRepository
from app.capabilities.monitoring.command_service import CommandService
from app.capabilities.investigation.read_service import InvestigationReadService
from app.capabilities.knowledge.source_service import KnowledgeSourceService
from app.capabilities.monitoring.profile_service import MonitoringProfileService
from app.capabilities.remediation.service.remediation_service import RemediationService
from app.capabilities.remediation.issue_fingerprint_service import IssueFingerprintService
from app.capabilities.monitoring.report_query_service import ReportQueryService
from app.capabilities.monitoring.server_service import ServerService
from app.capabilities.investigation.specialist_service import SpecialistDefinitionService
from app.capabilities.monitoring.scheduler.monitoring_scheduler import MonitoringScheduler
from app.capabilities.monitoring.service.monitoring_service import MonitoringService
from app.interfaces.mcp.registry import ProjectMcpToolBoundary


@dataclass(slots=True)
class ApplicationContainer:
    """
    يجمع حزم الاعتماديات الأساسية والتحليل والاسترجاع والتحقيق ووقت التشغيل في كائن واحد.
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
    investigation_backlog_worker: InvestigationBacklogWorker | None

    report_analyzer: ReportAnalyzer | None
    analysis_orchestrator: AnalysisOrchestrator | None
    report_pdf_service: ReportPdfService | None
    embedding_client: EmbeddingClient | None


__all__ = [
    "ApplicationContainer",
]
