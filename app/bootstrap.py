from app.domain.investigation.specialist_investigation_loop import (
    SpecialistInvestigationLoop,
)
from app.runtime.claude.job_service import (
    ClaudeAgentJobService,
)
from app.runtime.claude.monitoring_cycle import (
    ClaudeSupervisedMonitoringCycle,
)
from app.runtime.claude.multi_specialist_supervision import (
    ClaudeMultiSpecialistSupervisor,
)
from app.runtime.claude.supervisor import (
    ClaudeSupervisor,
)
from app.runtime.claude.native_monitoring import (
    ClaudeNativeMonitoringRunner,
)
from app.runtime.claude.ollama_runtime import (
    OllamaClaudeCommandBuilder,
)
from app.runtime.claude.runtime import (
    ClaudeRuntimeAdapter,
)
from app.runtime.claude.session_runner import (
    SubprocessClaudeSessionRunner,
)
from app.tools.project_boundary import (
    ProjectMcpToolBoundary,
)
from app.shared.database.repositories.agent_job_repository import (
    AgentJobRepository,
)
from app.shared.database.repositories.remediation_repository import (
    RemediationRepository,
)
from app.shared.services.remediation_service import (
    RemediationService,
)
from app.domain.investigation.server_coordinator import (
    ServerCoordinator,
)
from app.domain.investigation.specialist_context import (
    SpecialistContextBuilder,
)
from app.domain.investigation.specialist_reasoning_agent import (
    SpecialistReasoningAgent,
)
from app.domain.investigation.specialist_reasoning_client import (
    create_specialist_reasoning_client,
)
from app.domain.knowledge.retrieval import (
    KnowledgeHybridRetriever,
)
from app.shared.database.repositories.knowledge_retrieval_repository import (
    KnowledgeRetrievalRepository,
)
from app.domain.investigation.evidence_collection import (
    EvidenceCollectionService,
)
from app.domain.investigation.diagnostic_policy import (
    DiagnosticPolicyEngine,
)
from app.domain.investigation.diagnostic_tools import (
    DiagnosticToolRegistry,
    build_default_diagnostic_tool_registry,
)
from app.domain.knowledge.chunker import (
    StructureAwareKnowledgeChunker,
)
from app.domain.knowledge.chunking_service import (
    KnowledgeChunkingService,
)
from app.domain.knowledge.ingestion_service import (
    KnowledgeIngestionService,
)
from app.domain.knowledge.parsers import (
    KnowledgeContentParser,
)
from app.domain.knowledge.source_loader import (
    KnowledgeSourceLoader,
)
from app.shared.database.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.domain.knowledge.source_registry import (
    KnowledgeSourceRegistry,
)
from app.shared.database.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)
from app.shared.services.knowledge_source_service import (
    KnowledgeSourceService,
)
from app.shared.services.investigation_read_service import (
    InvestigationReadService,
)
from app.domain.investigation.runtime_snapshot_service import (
    InvestigationRuntimeSnapshotService,
)
from app.domain.investigation.persistence_service import (
    InvestigationPersistenceService,
)
from app.shared.database.repositories.investigation_repository import (
    InvestigationRepository,
)
from app.domain.investigation.investigation_router import (
    InvestigationRouter,
)
from app.domain.investigation.specialist_registry import (
    SpecialistRegistry,
)
from app.shared.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)
from app.shared.services.specialist_service import (
    SpecialistDefinitionService,
)
import logging
from dataclasses import dataclass

from app.admin.services.ssh_test_service import (
    SSHTestService,
)
from app.domain.analysis.analysis_agent_manager import (
    AnalysisAgentManager,
)
from app.domain.analysis.client_factory import (
    create_llm_analysis_client,
)
from app.domain.analysis.report_analyzer import (
    ReportAnalyzer,
)
from app.domain.analysis.analysis_orchestrator import (
    AnalysisOrchestrator,
)
from app.domain.analysis.retrieval.embedding_factory import (
    create_embedding_client,
)
from app.domain.analysis.retrieval.context_builder import (
    RagContextBuilder,
)
from app.domain.analysis.retrieval.rag_retriever import (
    RagRetriever,
)
from app.domain.analysis.retrieval.retrieval_indexer import (
    RetrievalIndexer,
)
from app.domain.analysis.retrieval.full_text_retriever import (
    FullTextRetriever,
)
from app.domain.analysis.retrieval.hybrid_retriever import (
    HybridRetriever,
)
from app.domain.analysis.retrieval.structured_compatibility import (
    StructuredCompatibilityChecker,
)
from app.admin.services.report_pdf_service import (
    ReportPdfService,
)
from app.shared.database.repositories.analysis_source_repository import (
    AnalysisSourceRepository,
)
from app.shared.database.repositories.retrieval_repository import (
    RetrievalRepository,
)
from app.tools.monitoring.service import (
    MonitoringService,
)
from app.tools.monitoring.scheduler import MonitoringScheduler
from app.shared.config import PROJECT_ROOT, settings
from app.shared.database.repositories.analysis_repository import (
    AnalysisRepository,
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
from app.shared.database.repositories.server_repository import (
    ServerRepository,
)
from app.shared.services.command_service import (
    CommandService,
)
from app.shared.services.profile_service import (
    MonitoringProfileService,
)
from app.shared.services.report_service import (
    ReportQueryService,
)
from app.shared.services.server_service import (
    ServerService,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ApplicationContainer:
    # Repositories
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

    # Shared services
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
    server_coordinator: ServerCoordinator | None
    claude_agent_job_service: ClaudeAgentJobService
    project_mcp_tool_boundary: ProjectMcpToolBoundary
    claude_supervised_monitoring_cycle: ClaudeSupervisedMonitoringCycle
    claude_multi_specialist_supervisor: ClaudeMultiSpecialistSupervisor
    claude_supervisor: ClaudeSupervisor

    # Admin services
    ssh_test_service: SSHTestService

    # Monitoring agent
    monitoring_service: MonitoringService
    scheduler: MonitoringScheduler

    # LLM analysis
    report_analyzer: ReportAnalyzer | None
    analysis_orchestrator: AnalysisOrchestrator | None
    analysis_agent_manager: AnalysisAgentManager | None
    report_pdf_service: ReportPdfService | None


def build_container() -> ApplicationContainer:
    """
    يبني جميع اعتماديات التطبيق في مكان واحد.

    لا يجب إنشاء Repositories أو Services داخل Routes
    أو داخل الوكيل مباشرة.
    """

    logger.info(
        "RAG policy | %s",
        settings.rag_policy_summary,
    )

    # -------------------------------------------------
    # Repositories
    # -------------------------------------------------

    server_repository = ServerRepository()
    command_repository = CommandRepository()
    profile_repository = MonitoringProfileRepository()
    report_repository = ReportRepository()
    analysis_repository = AnalysisRepository()
    retrieval_repository = RetrievalRepository()
    analysis_source_repository = AnalysisSourceRepository()
    specialist_definition_repository = SpecialistDefinitionRepository()
    investigation_repository = InvestigationRepository()
    knowledge_source_repository = KnowledgeSourceRepository()
    knowledge_document_repository = KnowledgeDocumentRepository()
    agent_job_repository = AgentJobRepository()
    remediation_repository = RemediationRepository()

    # -------------------------------------------------
    # Shared services
    # -------------------------------------------------

    server_service = ServerService(
        repository=server_repository,
    )

    command_service = CommandService(
        command_repository=command_repository,
        server_repository=server_repository,
    )

    monitoring_profile_service = (
        MonitoringProfileService(
            profile_repository=profile_repository,
            command_repository=command_repository,
            server_repository=server_repository,
        )
    )

    report_query_service = ReportQueryService(
        repository=report_repository,
    )

    specialist_definition_service = (
        SpecialistDefinitionService(
            repository=specialist_definition_repository,
        )
    )

    specialist_registry = SpecialistRegistry(
        repository=specialist_definition_repository,
    )

    investigation_router = InvestigationRouter(
        specialist_registry=specialist_registry,
        candidate_limit=12,
        selection_limit=4,
    )

    investigation_persistence_service = InvestigationPersistenceService(
        repository=investigation_repository,
    )

    investigation_read_service = InvestigationReadService(
        repository=investigation_repository,
    )

    investigation_runtime_snapshot_service = (
        InvestigationRuntimeSnapshotService(
            repository=investigation_repository,
        )
    )

    knowledge_source_service = KnowledgeSourceService(
        repository=knowledge_source_repository,
    )

    knowledge_source_registry = KnowledgeSourceRegistry(
        repository=knowledge_source_repository,
    )

    knowledge_ingestion_service = KnowledgeIngestionService(
        source_repository=knowledge_source_repository,
        document_repository=knowledge_document_repository,
        loader=KnowledgeSourceLoader(),
        parser=KnowledgeContentParser(),
    )

    knowledge_chunking_service = KnowledgeChunkingService(
        document_repository=knowledge_document_repository,
        chunker=StructureAwareKnowledgeChunker(),
    )

    diagnostic_tool_registry = (
        build_default_diagnostic_tool_registry()
    )

    diagnostic_policy_engine = DiagnosticPolicyEngine(
        registry=diagnostic_tool_registry,
    )

    evidence_collection_service = EvidenceCollectionService(
        server_repository=server_repository,
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
        repository=agent_job_repository,
    )

    remediation_service = RemediationService(
        repository=remediation_repository,
        automatic_remediation_allowed=False,
    )

    embedding_client = None
    retrieval_indexer = None
    vector_retriever = None
    full_text_retriever = None
    compatibility_checker = None
    rag_retriever = None
    rag_context_builder = None
    report_pdf_service = None
    specialist_investigation_loop = None
    server_coordinator = None

    try:
        report_pdf_service = ReportPdfService(
            font_path=settings.pdf_font_path,
        )
    except FileNotFoundError:
        logger.exception(
            "PDF service disabled because font was not found."
        )

    if settings.rag_vector_enabled:
        embedding_client = create_embedding_client(
            settings
        )
        retrieval_indexer = RetrievalIndexer(
            analysis_repository=analysis_repository,
            retrieval_repository=retrieval_repository,
            embedding_client=embedding_client,
        )
        vector_retriever = RagRetriever(
            embedding_client=embedding_client,
            retrieval_repository=retrieval_repository,
            analysis_repository=analysis_repository,
            top_k=settings.rag_top_k,
            minimum_score=(
                settings.rag_minimum_similarity
            ),
            hnsw_ef_search=(
                settings.rag_hnsw_ef_search
            ),
        )

    if settings.rag_full_text_enabled:
        full_text_retriever = FullTextRetriever(
            retrieval_repository=retrieval_repository,
            candidate_limit=(
                settings.rag_full_text_candidate_limit
            ),
            minimum_rank=(
                settings.rag_full_text_minimum_rank
            ),
        )

    if (
        settings.rag_assisted_enabled
        and (
            vector_retriever is not None
            or full_text_retriever is not None
        )
    ):
        if settings.rag_structured_compatibility_enabled:
            compatibility_checker = StructuredCompatibilityChecker()

        rag_retriever = HybridRetriever(
            analysis_repository=analysis_repository,
            retrieval_repository=retrieval_repository,
            compatibility_checker=compatibility_checker,
            vector_retriever=vector_retriever,
            full_text_retriever=full_text_retriever,
            top_k=settings.rag_context_top_k,
            rrf_k=settings.rag_rrf_k,
            minimum_vector_score=(
                settings.rag_minimum_similarity
            ),
        )
        rag_context_builder = RagContextBuilder()

    # -------------------------------------------------
    # Admin services
    # -------------------------------------------------

    ssh_test_service = SSHTestService(
        server_repository=server_repository,
        default_private_key_path=str(
            settings.default_ssh_private_key_path
        ),
        known_hosts_path=str(
            settings.ssh_known_hosts_path
        ),
        connect_timeout_seconds=(
            settings.ssh_connect_timeout_seconds
        ),
        command_timeout_seconds=(
            settings.command_timeout_seconds
        ),
    )

    # -------------------------------------------------
    # LLM analysis
    # -------------------------------------------------

    report_analyzer: ReportAnalyzer | None = None

    analysis_orchestrator: (
        AnalysisOrchestrator | None
    ) = None

    analysis_agent_manager: (
        AnalysisAgentManager | None
    ) = None

    if settings.llm_enabled:
        llm_client = create_llm_analysis_client(
            settings
        )

        specialist_knowledge_retriever = KnowledgeHybridRetriever(
            repository=KnowledgeRetrievalRepository(),
            embedding_client=create_embedding_client(
                settings
            ),
            hnsw_ef_search=(
                settings.rag_hnsw_ef_search
            ),
        )

        specialist_context_builder = SpecialistContextBuilder(
            knowledge_retriever=(
                specialist_knowledge_retriever
            )
        )

        specialist_reasoning_agent = SpecialistReasoningAgent(
            client=create_specialist_reasoning_client(
                settings
            )
        )

        specialist_investigation_loop = SpecialistInvestigationLoop(
            context_builder=(
                specialist_context_builder
            ),
            reasoning_agent=(
                specialist_reasoning_agent
            ),
            diagnostic_tool_registry=(
                diagnostic_tool_registry
            ),
            diagnostic_policy_engine=(
                diagnostic_policy_engine
            ),
            evidence_collection_service=(
                evidence_collection_service
            ),
        )

        server_coordinator = ServerCoordinator(
            specialist_registry=specialist_registry,
            specialist_loop=(
                specialist_investigation_loop
            ),
        )

        report_analyzer = ReportAnalyzer(
            report_query_service=report_query_service,
            analysis_repository=analysis_repository,
            llm_client=llm_client,
            max_report_characters=(
                settings.llm_max_report_characters
            ),
        )

        analysis_orchestrator = (
            AnalysisOrchestrator(
                report_query_service=(
                    report_query_service
                ),
                analysis_repository=(
                    analysis_repository
                ),
                report_analyzer=report_analyzer,
                exact_reuse_enabled=(
                    settings.rag_exact_reuse_enabled
                ),
                retrieval_indexer=retrieval_indexer,
                rag_retriever=rag_retriever,
                rag_context_builder=rag_context_builder,
                analysis_source_repository=(
                    analysis_source_repository
                ),
                rag_assisted_enabled=(
                    settings.rag_assisted_enabled
                ),
            )
        )

        analysis_agent_manager = (
            AnalysisAgentManager(
                analysis_orchestrator=(
                    analysis_orchestrator
                ),
                analysis_repository=(
                    analysis_repository
                ),
                queue_size_per_server=(
                    settings
                    .llm_analysis_queue_size_per_server
                ),
            )
        )

    # -------------------------------------------------
    # Monitoring agent
    # -------------------------------------------------

    monitoring_service = MonitoringService(
        server_repository=server_repository,
        profile_repository=profile_repository,
        report_repository=report_repository,
        analysis_agent_manager=(
            analysis_agent_manager
        ),
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

    project_mcp_tool_boundary = ProjectMcpToolBoundary(
        server_service=server_service,
        monitoring_profile_service=(
            monitoring_profile_service
        ),
        monitoring_service=monitoring_service,
        report_query_service=report_query_service,
        analysis_orchestrator=analysis_orchestrator,
        analysis_repository=analysis_repository,
        incident_retriever=rag_retriever,
        knowledge_retriever=(
            specialist_knowledge_retriever
            if settings.llm_enabled
            else None
        ),
        investigation_router=investigation_router,
        investigation_persistence_service=(
            investigation_persistence_service
        ),
        investigation_read_service=(
            investigation_read_service
        ),
        specialist_registry=specialist_registry,
        specialist_investigation_loop=(
            specialist_investigation_loop
        ),
        remediation_service=remediation_service,
    )

    claude_supervised_monitoring_cycle = (
        ClaudeSupervisedMonitoringCycle(
            tool_boundary=project_mcp_tool_boundary,
            agent_job_service=(
                claude_agent_job_service
            ),
        )
    )

    claude_multi_specialist_supervisor = (
        ClaudeMultiSpecialistSupervisor(
            tool_boundary=project_mcp_tool_boundary,
            agent_job_service=(
                claude_agent_job_service
            ),
        )
    )

    claude_supervisor_runner = (
        claude_supervised_monitoring_cycle
    )

    if settings.claude_runtime_enabled:
        claude_command_builder = (
            OllamaClaudeCommandBuilder(
                project_root=PROJECT_ROOT,
                model=(
                    settings.effective_claude_runtime_model
                ),
                base_url=settings.ollama_base_url,
                executable=(
                    settings.claude_runtime_executable
                ),
                agent=settings.claude_runtime_agent,
            )
        )
        claude_session_runner = (
            SubprocessClaudeSessionRunner(
                command_builder=claude_command_builder,
                project_root=PROJECT_ROOT,
            )
        )
        claude_runtime_adapter = ClaudeRuntimeAdapter(
            runner=claude_session_runner,
            operational_tools_enabled=True,
        )
        claude_supervisor_runner = (
            ClaudeNativeMonitoringRunner(
                runtime_adapter=claude_runtime_adapter,
                agent_job_service=claude_agent_job_service,
                timeout_seconds=(
                    settings.claude_runtime_timeout_seconds
                ),
                max_turns=(
                    settings.claude_runtime_max_turns
                ),
            )
        )

    claude_supervisor = ClaudeSupervisor(
        runner=claude_supervisor_runner,
    )

    scheduler = MonitoringScheduler(
        server_repository=server_repository,
        monitoring_service=claude_supervisor,
        polling_interval_seconds=(
            settings.monitor_polling_interval_seconds
        ),
        max_concurrent_servers=(
            settings.max_concurrent_servers
        ),
    )

    return ApplicationContainer(
        server_repository=server_repository,
        command_repository=command_repository,
        profile_repository=profile_repository,
        report_repository=report_repository,
        analysis_repository=analysis_repository,
        analysis_source_repository=(
            analysis_source_repository
        ),
        specialist_definition_repository=(
            specialist_definition_repository
        ),
        investigation_repository=(
            investigation_repository
        ),
        knowledge_source_repository=(
            knowledge_source_repository
        ),
        knowledge_document_repository=(
            knowledge_document_repository
        ),
        agent_job_repository=agent_job_repository,
        remediation_repository=remediation_repository,
        server_service=server_service,
        command_service=command_service,
        monitoring_profile_service=(
            monitoring_profile_service
        ),
        report_query_service=report_query_service,
        specialist_definition_service=(
            specialist_definition_service
        ),
        specialist_registry=(
            specialist_registry
        ),
        investigation_router=(
            investigation_router
        ),
        investigation_persistence_service=(
            investigation_persistence_service
        ),
        investigation_read_service=investigation_read_service,
        investigation_runtime_snapshot_service=investigation_runtime_snapshot_service,
        knowledge_source_service=(
            knowledge_source_service
        ),
        knowledge_source_registry=(
            knowledge_source_registry
        ),
        knowledge_ingestion_service=(
            knowledge_ingestion_service
        ),

        knowledge_chunking_service=(
            knowledge_chunking_service
        ),
        diagnostic_tool_registry=(
            diagnostic_tool_registry
        ),
        diagnostic_policy_engine=(
            diagnostic_policy_engine
        ),
        evidence_collection_service=(
            evidence_collection_service
        ),
        remediation_service=remediation_service,
        specialist_investigation_loop=(
            specialist_investigation_loop
        ),
        server_coordinator=(
            server_coordinator
        ),
        claude_agent_job_service=(
            claude_agent_job_service
        ),
        project_mcp_tool_boundary=(
            project_mcp_tool_boundary
        ),
        claude_supervised_monitoring_cycle=(
            claude_supervised_monitoring_cycle
        ),
        claude_multi_specialist_supervisor=(
            claude_multi_specialist_supervisor
        ),
        claude_supervisor=claude_supervisor,
        ssh_test_service=ssh_test_service,
        monitoring_service=monitoring_service,
        scheduler=scheduler,
        report_analyzer=report_analyzer,
        analysis_orchestrator=analysis_orchestrator,
        analysis_agent_manager=(
            analysis_agent_manager
        ),
        report_pdf_service=report_pdf_service,
    )


container = build_container()
