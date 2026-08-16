"""
يركب dependencies ويربط repositories والخدمات والـruntime.

الموقع في المعمارية: Bootstrap / dependency composition.
يُستدعى بواسطة: app.main أو الاختبارات عند إنشاء container.
يعتمد مباشرة على: app.infrastructure.database.repositories.server_repository، app.infrastructure.database.repositories.command_repository، app.infrastructure.database.repositories.profile_repository، app.infrastructure.database.repositories.report_repository، app.infrastructure.database.repositories.analysis_repository، app.infrastructure.database.repositories.retrieval_repository.
الحد المعماري: لا ينفذ workflow business؛ دوره wiring وترتيب الإنشاء.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.infrastructure.database.repositories.server_repository import (
    ServerRepository,
)
from app.infrastructure.database.repositories.command_repository import (
    CommandRepository,
)
from app.infrastructure.database.repositories.profile_repository import (
    MonitoringProfileRepository,
)
from app.infrastructure.database.repositories.report_repository import (
    ReportRepository,
)
from app.infrastructure.database.repositories.analysis_repository import (
    AnalysisRepository,
)
from app.infrastructure.database.repositories.retrieval_repository import (
    RetrievalRepository,
)
from app.infrastructure.database.repositories.analysis_source_repository import (
    AnalysisSourceRepository,
)
from app.infrastructure.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)
from app.infrastructure.database.repositories.investigation_repository import (
    InvestigationRepository,
)
from app.infrastructure.database.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)
from app.infrastructure.database.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.infrastructure.database.repositories.agent_job_repository import (
    AgentJobRepository,
)
from app.infrastructure.database.repositories.remediation_repository import (
    RemediationRepository,
)
from app.infrastructure.database.repositories.autonomous_remediation_repository import (
    AutonomousRemediationRepository,
)


@dataclass(slots=True, frozen=True)
class RepositoryBundle:
    """
    يمثل RepositoryBundle مسؤولية محددة داخل طبقة Bootstrap / dependency composition.

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
    retrieval_repository: RetrievalRepository
    analysis_source_repository: AnalysisSourceRepository
    specialist_definition_repository: SpecialistDefinitionRepository
    investigation_repository: InvestigationRepository
    knowledge_source_repository: KnowledgeSourceRepository
    knowledge_document_repository: KnowledgeDocumentRepository
    agent_job_repository: AgentJobRepository
    remediation_repository: RemediationRepository
    autonomous_remediation_repository: AutonomousRemediationRepository


def build_repositories() -> RepositoryBundle:
    """
    يبني DTO أو dependency graph من المدخلات ضمن طبقة Bootstrap / dependency composition.

    تُستدعى عندما يصل workflow إلى build_repositories؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد RepositoryBundle أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
        autonomous_remediation_repository=(
            AutonomousRemediationRepository()
        ),
    )


__all__ = [
    "RepositoryBundle",
    "build_repositories",
]
