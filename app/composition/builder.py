from app.composition.runtime import build_runtime_composition
from app.composition.analysis import (
    build_analysis_investigation_composition,
    build_retrieval_composition,
)
from app.composition.container import ApplicationContainer
from app.composition.services import build_core_services
from app.composition.repositories import build_repositories
import logging

from app.interfaces.admin.services.ssh_test_service import (
    SSHTestService,
)
from app.core.config import PROJECT_ROOT, settings

logger = logging.getLogger(__name__)




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

    repositories = build_repositories()
    server_repository = repositories.server_repository
    command_repository = repositories.command_repository
    profile_repository = repositories.profile_repository
    report_repository = repositories.report_repository
    analysis_repository = repositories.analysis_repository
    retrieval_repository = repositories.retrieval_repository
    analysis_source_repository = repositories.analysis_source_repository
    specialist_definition_repository = repositories.specialist_definition_repository
    investigation_repository = repositories.investigation_repository
    knowledge_source_repository = repositories.knowledge_source_repository
    knowledge_document_repository = repositories.knowledge_document_repository
    agent_job_repository = repositories.agent_job_repository
    remediation_repository = repositories.remediation_repository

    # -------------------------------------------------
    # Shared services
    # -------------------------------------------------

    services = build_core_services(
        repositories,
        settings,
    )
    server_service = services.server_service
    command_service = services.command_service
    monitoring_profile_service = services.monitoring_profile_service
    report_query_service = services.report_query_service
    specialist_definition_service = services.specialist_definition_service
    specialist_registry = services.specialist_registry
    investigation_router = services.investigation_router
    investigation_persistence_service = services.investigation_persistence_service
    investigation_read_service = services.investigation_read_service
    investigation_runtime_snapshot_service = services.investigation_runtime_snapshot_service
    specialist_execution_service = services.specialist_execution_service
    knowledge_source_service = services.knowledge_source_service
    knowledge_source_registry = services.knowledge_source_registry
    knowledge_ingestion_service = services.knowledge_ingestion_service
    knowledge_chunking_service = services.knowledge_chunking_service
    diagnostic_tool_registry = services.diagnostic_tool_registry
    diagnostic_policy_engine = services.diagnostic_policy_engine
    evidence_collection_service = services.evidence_collection_service
    claude_agent_job_service = services.claude_agent_job_service
    remediation_service = services.remediation_service

    retrieval_composition = build_retrieval_composition(
        repositories,
        settings,
    )
    rag_retriever = retrieval_composition.rag_retriever
    report_pdf_service = retrieval_composition.report_pdf_service

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

    analysis_composition = build_analysis_investigation_composition(
        repositories,
        services,
        retrieval_composition,
        settings,
    )
    specialist_knowledge_retriever = (
        analysis_composition.specialist_knowledge_retriever
    )
    specialist_investigation_loop = (
        analysis_composition.specialist_investigation_loop
    )
    report_analyzer = analysis_composition.report_analyzer
    analysis_orchestrator = analysis_composition.analysis_orchestrator

    # -------------------------------------------------
    # Monitoring agent
    # -------------------------------------------------

    runtime_composition = build_runtime_composition(
        repositories=repositories,
        services=services,
        retrieval=retrieval_composition,
        analysis=analysis_composition,
        settings=settings,
        project_root=PROJECT_ROOT,
    )
    monitoring_service = runtime_composition.monitoring_service
    project_mcp_tool_boundary = (
        runtime_composition.project_mcp_tool_boundary
    )
    claude_supervisor = runtime_composition.claude_supervisor
    scheduler = runtime_composition.scheduler

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
        specialist_execution_service=specialist_execution_service,
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
        claude_agent_job_service=(
            claude_agent_job_service
        ),
        project_mcp_tool_boundary=(
            project_mcp_tool_boundary
        ),
        claude_supervisor=claude_supervisor,
        ssh_test_service=ssh_test_service,
        monitoring_service=monitoring_service,
        scheduler=scheduler,
        report_analyzer=report_analyzer,
        analysis_orchestrator=analysis_orchestrator,
        report_pdf_service=report_pdf_service,
    )
