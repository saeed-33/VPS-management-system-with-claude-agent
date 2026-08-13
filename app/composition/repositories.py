from __future__ import annotations

from dataclasses import dataclass

from app.shared.database.repositories.server_repository import (
    ServerRepository,
)
from app.shared.database.repositories.command_repository import (
    CommandRepository,
)
from app.shared.database.repositories.profile_repository import (
    MonitoringProfileRepository,
)
from app.shared.database.repositories.report_repository import (
    ReportRepository,
)
from app.shared.database.repositories.analysis_repository import (
    AnalysisRepository,
)
from app.shared.database.repositories.retrieval_repository import (
    RetrievalRepository,
)
from app.shared.database.repositories.analysis_source_repository import (
    AnalysisSourceRepository,
)
from app.shared.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)
from app.shared.database.repositories.investigation_repository import (
    InvestigationRepository,
)
from app.shared.database.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)
from app.shared.database.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.shared.database.repositories.agent_job_repository import (
    AgentJobRepository,
)
from app.shared.database.repositories.remediation_repository import (
    RemediationRepository,
)


@dataclass(slots=True, frozen=True)
class RepositoryBundle:
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


def build_repositories() -> RepositoryBundle:
    return RepositoryBundle(
        server_repository=(
            ServerRepository()
        ),
        command_repository=(
            CommandRepository()
        ),
        profile_repository=(
            MonitoringProfileRepository()
        ),
        report_repository=(
            ReportRepository()
        ),
        analysis_repository=(
            AnalysisRepository()
        ),
        retrieval_repository=(
            RetrievalRepository()
        ),
        analysis_source_repository=(
            AnalysisSourceRepository()
        ),
        specialist_definition_repository=(
            SpecialistDefinitionRepository()
        ),
        investigation_repository=(
            InvestigationRepository()
        ),
        knowledge_source_repository=(
            KnowledgeSourceRepository()
        ),
        knowledge_document_repository=(
            KnowledgeDocumentRepository()
        ),
        agent_job_repository=(
            AgentJobRepository()
        ),
        remediation_repository=(
            RemediationRepository()
        ),
    )


__all__ = [
    "RepositoryBundle",
    "build_repositories",
]
