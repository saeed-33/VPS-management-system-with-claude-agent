from __future__ import annotations

from dataclasses import dataclass

from app.admin.services.report_pdf_service import ReportPdfService
from app.admin.services.ssh_test_service import SSHTestService
from app.domain.analysis.analysis_orchestrator import AnalysisOrchestrator
from app.domain.analysis.report_analyzer import ReportAnalyzer
from app.domain.investigation.diagnostic_policy import DiagnosticPolicyEngine
from app.domain.investigation.diagnostic_tools import DiagnosticToolRegistry
from app.domain.investigation.evidence_collection import EvidenceCollectionService
from app.domain.investigation.investigation_router import InvestigationRouter
from app.domain.investigation.persistence_service import InvestigationPersistenceService
from app.domain.investigation.runtime_snapshot_service import InvestigationRuntimeSnapshotService
from app.domain.investigation.specialist_investigation_loop import SpecialistInvestigationLoop
from app.domain.investigation.specialist_registry import SpecialistRegistry
from app.domain.knowledge.chunking_service import KnowledgeChunkingService
from app.domain.knowledge.ingestion_service import KnowledgeIngestionService
from app.domain.knowledge.source_registry import KnowledgeSourceRegistry
from app.runtime.claude.job_service import ClaudeAgentJobService
from app.runtime.claude.supervisor import ClaudeSupervisor
from app.shared.database.repositories.agent_job_repository import AgentJobRepository
from app.shared.database.repositories.analysis_repository import AnalysisRepository
from app.shared.database.repositories.analysis_source_repository import AnalysisSourceRepository
from app.shared.database.repositories.command_repository import CommandRepository
from app.shared.database.repositories.investigation_repository import InvestigationRepository
from app.shared.database.repositories.knowledge_document_repository import KnowledgeDocumentRepository
from app.shared.database.repositories.knowledge_source_repository import KnowledgeSourceRepository
from app.shared.database.repositories.profile_repository import MonitoringProfileRepository
from app.shared.database.repositories.remediation_repository import RemediationRepository
from app.shared.database.repositories.report_repository import ReportRepository
from app.shared.database.repositories.server_repository import ServerRepository
from app.shared.database.repositories.specialist_definition_repository import SpecialistDefinitionRepository
from app.shared.services.command_service import CommandService
from app.shared.services.investigation_read_service import InvestigationReadService
from app.shared.services.knowledge_source_service import KnowledgeSourceService
from app.shared.services.profile_service import MonitoringProfileService
from app.shared.services.remediation_service import RemediationService
from app.shared.services.report_service import ReportQueryService
from app.shared.services.server_service import ServerService
from app.shared.services.specialist_service import SpecialistDefinitionService
from app.tools.monitoring.scheduler import MonitoringScheduler
from app.tools.monitoring.service import MonitoringService
from app.tools.project_boundary import ProjectMcpToolBoundary


@dataclass(slots=True)
class ApplicationContainer:
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
    knowledge_source_service: KnowledgeSourceService
    knowledge_source_registry: KnowledgeSourceRegistry
    knowledge_ingestion_service: KnowledgeIngestionService
    knowledge_chunking_service: KnowledgeChunkingService
    diagnostic_tool_registry: DiagnosticToolRegistry
    diagnostic_policy_engine: DiagnosticPolicyEngine
    evidence_collection_service: EvidenceCollectionService
    remediation_service: RemediationService
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
