"""حزمة مستودعات التطبيق التي تُشاركها الخدمات."""
from __future__ import annotations

from dataclasses import dataclass

from app.infrastructure.database.repositories.agent_job_repository import AgentJobRepository
from app.infrastructure.database.repositories.analysis_repository.repository import AnalysisRepository
from app.infrastructure.database.repositories.analysis_source_repository import AnalysisSourceRepository
from app.infrastructure.database.repositories.autonomous_remediation_repository.repository import AutonomousRemediationRepository
from app.infrastructure.database.repositories.command_repository.repository import CommandRepository
from app.infrastructure.database.repositories.investigation_repository.repository import InvestigationRepository
from app.infrastructure.database.repositories.knowledge_document_repository import KnowledgeDocumentRepository
from app.infrastructure.database.repositories.knowledge_source_repository import KnowledgeSourceRepository
from app.infrastructure.database.repositories.profile_repository.repository import MonitoringProfileRepository
from app.infrastructure.database.repositories.remediation_repository.repository import RemediationRepository
from app.infrastructure.database.repositories.report_repository import ReportRepository
from app.infrastructure.database.repositories.retrieval_repository import RetrievalRepository
from app.infrastructure.database.repositories.server_repository import ServerRepository
from app.infrastructure.database.repositories.specialist_definition_repository import SpecialistDefinitionRepository


@dataclass(slots=True, frozen=True)
class RepositoryBundle:
    """يمثل جميع مستودعات التطبيق المبنية مرة واحدة."""

    server_repository: ServerRepository
    command_repository: CommandRepository
    profile_repository: MonitoringProfileRepository
    report_repository: ReportRepository
    analysis_repository: AnalysisRepository
    retrieval_repository: RetrievalRepository
    analysis_source_repository: AnalysisSourceRepository
    specialist_definition_repository: SpecialistDefinitionRepository
    investigation_repository: InvestigationRepository
    knowledge_source_repository: KnowledgeSourceRepository
    knowledge_document_repository: KnowledgeDocumentRepository
    agent_job_repository: AgentJobRepository
    remediation_repository: RemediationRepository
    autonomous_remediation_repository: AutonomousRemediationRepository
