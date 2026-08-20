"""
تركيب حزمة خدمات المجال الأساسية.

ينشئ خدمات المراقبة والتقارير والأوامر والملفات والتحقيق والمعالجة، ويمرر إليها
المستودعات والسياسات والعملاء التي تحتاجها.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.composition.repositories import RepositoryBundle
from app.core.policies.diagnostic_policy.diagnostic_policy_engine import DiagnosticPolicyEngine
from app.core.policies.diagnostic_tools.diagnostic_tool_registry import DiagnosticToolRegistry
from app.core.policies.diagnostic_tools.factories import build_default_diagnostic_tool_registry
from app.capabilities.investigation.evidence_collection.evidence_collection_service import EvidenceCollectionService
from app.capabilities.investigation.investigation_router.investigation_router import InvestigationRouter
from app.capabilities.investigation.persistence_service import InvestigationPersistenceService
from app.capabilities.investigation.runtime_snapshot_service.service import InvestigationRuntimeSnapshotService
from app.capabilities.investigation.specialist_execution_service.specialist_execution_service import SpecialistExecutionService
from app.capabilities.investigation.correlation.cross_specialist_correlator import CrossSpecialistCorrelator
from app.capabilities.investigation.final_diagnosis_synthesizer.service import FinalDiagnosisSynthesizer
from app.capabilities.investigation.specialist_registry.specialist_registry import SpecialistRegistry
from app.capabilities.knowledge.chunker.chunker import StructureAwareKnowledgeChunker
from app.capabilities.knowledge.chunking_service import KnowledgeChunkingService
from app.capabilities.knowledge.ingestion_service import KnowledgeIngestionService
from app.capabilities.knowledge.parsers.content_parser import KnowledgeContentParser
from app.capabilities.knowledge.source_loader.loader import KnowledgeSourceLoader
from app.capabilities.knowledge.source_registry.registry import KnowledgeSourceRegistry
from app.runtime.claude.job_service import ClaudeAgentJobService
from app.core.config import Settings
from app.capabilities.monitoring.command_service import CommandService
from app.capabilities.investigation.read_service import InvestigationReadService
from app.capabilities.knowledge.source_service import KnowledgeSourceService
from app.capabilities.monitoring.profile_service import MonitoringProfileService
from app.capabilities.remediation.service.service import RemediationService
from app.capabilities.remediation.sandbox_runtime import NativeSandboxRuntime
from app.capabilities.remediation.plan_proposal_service import RemediationPlanProposalService
from app.capabilities.remediation.issue_fingerprint_service import IssueFingerprintService
from app.capabilities.remediation.autonomous_policy_service import AutonomousPolicyService
from app.capabilities.remediation.autonomous_history_service import AutonomousHistoryService
from app.capabilities.remediation.autonomous_candidate_service import AutonomousCandidateService
from app.capabilities.remediation.autonomous_authorization_service import AutonomousAuthorizationService
from app.capabilities.remediation.autonomous_execution_service.service import AutonomousExecutionService
from app.capabilities.remediation.execution.ssh_service_state_evidence_collector import SSHServiceStateEvidenceCollector
from app.capabilities.remediation.execution.ssh_named_write_runner import SSHNamedWriteRunner
from app.capabilities.remediation.execution.ssh_service_verifier import SSHServiceVerifier
from app.capabilities.monitoring.report_query_service import ReportQueryService
from app.capabilities.monitoring.server_service import ServerService
from app.capabilities.investigation.specialist_service import SpecialistDefinitionService


@dataclass(slots=True, frozen=True)
class CoreServiceBundle:
    """
    يمثل خدمات المجال الأساسية الجاهزة للحقن في طبقات API ووقت التشغيل.
    """
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


def build_core_services(
    repositories: RepositoryBundle,
    settings: Settings,
) -> CoreServiceBundle:
    """
    ينشئ خدمات المراقبة والتقارير والتحقيق والمعالجة ويدمجها في حزمة الخدمات الأساسية.
    """
    server_service = ServerService(
        repository=repositories.server_repository,
    )
    command_service = CommandService(
        command_repository=repositories.command_repository,
        server_repository=repositories.server_repository,
    )
    monitoring_profile_service = MonitoringProfileService(
        profile_repository=repositories.profile_repository,
        command_repository=repositories.command_repository,
        server_repository=repositories.server_repository,
    )
    report_query_service = ReportQueryService(
        repository=repositories.report_repository,
    )
    specialist_definition_service = SpecialistDefinitionService(
        repository=repositories.specialist_definition_repository,
    )
    specialist_registry = SpecialistRegistry(
        repository=repositories.specialist_definition_repository,
    )
    investigation_router = InvestigationRouter(
        specialist_registry=specialist_registry,
        candidate_limit=12,
        selection_limit=4,
    )
    investigation_persistence_service = InvestigationPersistenceService(
        repository=repositories.investigation_repository,
    )
    investigation_read_service = InvestigationReadService(
        repository=repositories.investigation_repository,
    )
    investigation_runtime_snapshot_service = InvestigationRuntimeSnapshotService(
        repository=repositories.investigation_repository,
    )
    knowledge_source_service = KnowledgeSourceService(
        repository=repositories.knowledge_source_repository,
    )
    knowledge_source_registry = KnowledgeSourceRegistry(
        repository=repositories.knowledge_source_repository,
    )
    knowledge_ingestion_service = KnowledgeIngestionService(
        source_repository=repositories.knowledge_source_repository,
        document_repository=repositories.knowledge_document_repository,
        loader=KnowledgeSourceLoader(),
        parser=KnowledgeContentParser(),
    )
    knowledge_chunking_service = KnowledgeChunkingService(
        document_repository=repositories.knowledge_document_repository,
        chunker=StructureAwareKnowledgeChunker(),
    )
    diagnostic_tool_registry = build_default_diagnostic_tool_registry()
    diagnostic_policy_engine = DiagnosticPolicyEngine(
        registry=diagnostic_tool_registry,
    )
    evidence_collection_service = EvidenceCollectionService(
        server_repository=repositories.server_repository,
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
    claude_agent_job_service = ClaudeAgentJobService(
        repository=repositories.agent_job_repository,
    )
    issue_fingerprint_service = IssueFingerprintService(
        investigation_read_service=investigation_read_service,
    )
    remediation_service = RemediationService(
        repository=repositories.remediation_repository,
        automatic_remediation_allowed=settings.automatic_remediation_allowed,
        write_runner=SSHNamedWriteRunner(
            server_repository=repositories.server_repository,
            private_key_path=str(settings.default_ssh_private_key_path),
            known_hosts_path=str(settings.ssh_known_hosts_path),
            connect_timeout_seconds=settings.ssh_connect_timeout_seconds,
            command_timeout_seconds=settings.command_timeout_seconds,
        ),
        verification_runner=SSHServiceVerifier(
            server_repository=repositories.server_repository,
            private_key_path=str(settings.default_ssh_private_key_path),
            known_hosts_path=str(settings.ssh_known_hosts_path),
            connect_timeout_seconds=settings.ssh_connect_timeout_seconds,
            command_timeout_seconds=settings.command_timeout_seconds,
        ),
        evidence_collector=SSHServiceStateEvidenceCollector(
            server_repository=repositories.server_repository,
            private_key_path=str(settings.default_ssh_private_key_path),
            known_hosts_path=str(settings.ssh_known_hosts_path),
            connect_timeout_seconds=settings.ssh_connect_timeout_seconds,
            command_timeout_seconds=settings.command_timeout_seconds,
        ),
        server_repository=repositories.server_repository,
        sandbox_runtime=NativeSandboxRuntime(
            attestation_file=settings.phase6_native_sandbox_attestation_file,
            require_wsl2=settings.phase6_require_wsl2,
        ),
        issue_fingerprint_service=issue_fingerprint_service,
    )
    remediation_plan_proposal_service = RemediationPlanProposalService(
        repository=repositories.remediation_repository,
        remediation_service=remediation_service,
    )
    specialist_execution_service = SpecialistExecutionService(
        repository=repositories.investigation_repository,
        snapshot_service=investigation_runtime_snapshot_service,
        correlator=CrossSpecialistCorrelator(),
        synthesizer=FinalDiagnosisSynthesizer(),
        remediation_plan_proposal_service=remediation_plan_proposal_service,
    )
    autonomous_policy_service = AutonomousPolicyService(
        repository=repositories.autonomous_remediation_repository,
    )
    autonomous_history_service = AutonomousHistoryService(
        repository=repositories.autonomous_remediation_repository,
    )
    autonomous_candidate_service = AutonomousCandidateService(
        repository=repositories.autonomous_remediation_repository,
    )
    autonomous_authorization_service = AutonomousAuthorizationService(
        repository=repositories.autonomous_remediation_repository,
    )
    autonomous_execution_service = AutonomousExecutionService(
        repository=repositories.autonomous_remediation_repository,
        remediation_repository=repositories.remediation_repository,
        remediation_service=remediation_service,
        policy_service=autonomous_policy_service,
        history_service=autonomous_history_service,
        candidate_service=autonomous_candidate_service,
        authorization_service=autonomous_authorization_service,
        automatic_remediation_allowed=settings.automatic_remediation_allowed,
    )

    return CoreServiceBundle(
        server_service=server_service,
        command_service=command_service,
        monitoring_profile_service=monitoring_profile_service,
        report_query_service=report_query_service,
        specialist_definition_service=specialist_definition_service,
        specialist_registry=specialist_registry,
        investigation_router=investigation_router,
        investigation_persistence_service=investigation_persistence_service,
        investigation_read_service=investigation_read_service,
        investigation_runtime_snapshot_service=investigation_runtime_snapshot_service,
        specialist_execution_service=specialist_execution_service,
        knowledge_source_service=knowledge_source_service,
        knowledge_source_registry=knowledge_source_registry,
        knowledge_ingestion_service=knowledge_ingestion_service,
        knowledge_chunking_service=knowledge_chunking_service,
        diagnostic_tool_registry=diagnostic_tool_registry,
        diagnostic_policy_engine=diagnostic_policy_engine,
        evidence_collection_service=evidence_collection_service,
        claude_agent_job_service=claude_agent_job_service,
        issue_fingerprint_service=issue_fingerprint_service,
        remediation_service=remediation_service,
        autonomous_policy_service=autonomous_policy_service,
        autonomous_history_service=autonomous_history_service,
        autonomous_candidate_service=autonomous_candidate_service,
        autonomous_authorization_service=autonomous_authorization_service,
        autonomous_execution_service=autonomous_execution_service,
    )


__all__ = [
    "CoreServiceBundle",
    "build_core_services",
]
