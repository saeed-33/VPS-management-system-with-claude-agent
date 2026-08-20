"""حزمة الخدمات التي تُحقن في واجهات التطبيق ووقت التشغيل."""
from __future__ import annotations

from dataclasses import dataclass

from app.capabilities.investigation.evidence_collection.evidence_collection_service import EvidenceCollectionService
from app.capabilities.investigation.investigation_router.investigation_router import InvestigationRouter
from app.capabilities.investigation.persistence_service import InvestigationPersistenceService
from app.capabilities.investigation.read_service import InvestigationReadService
from app.capabilities.investigation.runtime_snapshot_service.runtime_snapshot_service import InvestigationRuntimeSnapshotService
from app.capabilities.investigation.specialist_execution_service.specialist_execution_service import SpecialistExecutionService
from app.capabilities.investigation.specialist_registry.specialist_registry import SpecialistRegistry
from app.capabilities.investigation.specialist_service import SpecialistDefinitionService
from app.capabilities.knowledge.chunking_service import KnowledgeChunkingService
from app.capabilities.knowledge.ingestion_service import KnowledgeIngestionService
from app.capabilities.knowledge.source_registry.registry import KnowledgeSourceRegistry
from app.capabilities.knowledge.source_service import KnowledgeSourceService
from app.capabilities.monitoring.command_service import CommandService
from app.capabilities.monitoring.profile_service import MonitoringProfileService
from app.capabilities.monitoring.report_query_service import ReportQueryService
from app.capabilities.monitoring.server_service import ServerService
from app.capabilities.remediation.autonomous_authorization_service import AutonomousAuthorizationService
from app.capabilities.remediation.autonomous_candidate_service import AutonomousCandidateService
from app.capabilities.remediation.autonomous_execution_service.autonomous_execution_service import AutonomousExecutionService
from app.capabilities.remediation.autonomous_history_service import AutonomousHistoryService
from app.capabilities.remediation.autonomous_policy_service import AutonomousPolicyService
from app.capabilities.remediation.service.remediation_service import RemediationService
from app.capabilities.remediation.issue_fingerprint_service import IssueFingerprintService
from app.core.policies.diagnostic_policy.diagnostic_policy_engine import DiagnosticPolicyEngine
from app.core.policies.diagnostic_tools.diagnostic_tool_registry import DiagnosticToolRegistry
from app.runtime.claude.job_service import ClaudeAgentJobService


@dataclass(slots=True, frozen=True)
class CoreServiceBundle:
    """يمثل خدمات المجال الأساسية الجاهزة للحقن."""

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
    claude_agent_job_service: ClaudeAgentJobService
    remediation_service: RemediationService
    issue_fingerprint_service: IssueFingerprintService
    autonomous_policy_service: AutonomousPolicyService
    autonomous_history_service: AutonomousHistoryService
    autonomous_candidate_service: AutonomousCandidateService
    autonomous_authorization_service: AutonomousAuthorizationService
    autonomous_execution_service: AutonomousExecutionService
