from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.composition.analysis import (
    AnalysisInvestigationComposition,
    RetrievalComposition,
)
from app.composition.repositories import RepositoryBundle
from app.composition.services import CoreServiceBundle
from app.runtime.claude.native_monitoring import ClaudeNativeMonitoringRunner
from app.runtime.claude.ollama_runtime import OllamaClaudeCommandBuilder
from app.runtime.claude.runtime import ClaudeRuntimeAdapter
from app.runtime.claude.session_runner import SubprocessClaudeSessionRunner
from app.runtime.claude.supervisor import ClaudeSupervisor
from app.core.config import Settings
from app.capabilities.monitoring.scheduler import MonitoringScheduler
from app.capabilities.monitoring.service import MonitoringService
from app.interfaces.mcp.registry import ProjectMcpToolBoundary


@dataclass(slots=True, frozen=True)
class RuntimeComposition:
    monitoring_service: MonitoringService
    project_mcp_tool_boundary: ProjectMcpToolBoundary
    claude_supervisor: ClaudeSupervisor
    scheduler: MonitoringScheduler


def build_runtime_composition(
    repositories: RepositoryBundle,
    services: CoreServiceBundle,
    retrieval: RetrievalComposition,
    analysis: AnalysisInvestigationComposition,
    settings: Settings,
    project_root: Path,
) -> RuntimeComposition:
    monitoring_service = MonitoringService(
        server_repository=repositories.server_repository,
        profile_repository=repositories.profile_repository,
        report_repository=repositories.report_repository,
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
        server_service=services.server_service,
        monitoring_profile_service=services.monitoring_profile_service,
        monitoring_service=monitoring_service,
        report_query_service=services.report_query_service,
        analysis_orchestrator=analysis.analysis_orchestrator,
        analysis_repository=repositories.analysis_repository,
        incident_retriever=retrieval.rag_retriever,
        knowledge_retriever=analysis.specialist_knowledge_retriever,
        investigation_router=services.investigation_router,
        investigation_persistence_service=(
            services.investigation_persistence_service
        ),
        investigation_read_service=services.investigation_read_service,
        specialist_registry=services.specialist_registry,
        specialist_investigation_loop=analysis.specialist_investigation_loop,
        specialist_execution_service=services.specialist_execution_service,
        remediation_service=services.remediation_service,
        autonomous_execution_service=services.autonomous_execution_service,
    )

    claude_supervisor_runner = None

    if settings.claude_runtime_enabled:
        claude_command_builder = OllamaClaudeCommandBuilder(
            project_root=project_root,
            model=settings.effective_claude_runtime_model,
            base_url=settings.ollama_base_url,
            executable=settings.claude_runtime_executable,
            agent=settings.claude_runtime_agent,
        )

        claude_session_runner = SubprocessClaudeSessionRunner(
            command_builder=claude_command_builder,
            project_root=project_root,
        )

        claude_runtime_adapter = ClaudeRuntimeAdapter(
            runner=claude_session_runner,
            operational_tools_enabled=True,
        )

        claude_supervisor_runner = ClaudeNativeMonitoringRunner(
            runtime_adapter=claude_runtime_adapter,
            agent_job_service=services.claude_agent_job_service,
            timeout_seconds=settings.claude_runtime_timeout_seconds,
            max_turns=settings.claude_runtime_max_turns,
        )

    claude_supervisor = ClaudeSupervisor(
        runner=claude_supervisor_runner,
    )

    scheduler = MonitoringScheduler(
        server_repository=repositories.server_repository,
        monitoring_service=claude_supervisor,
        polling_interval_seconds=(
            settings.monitor_polling_interval_seconds
        ),
        max_concurrent_servers=settings.max_concurrent_servers,
    )

    return RuntimeComposition(
        monitoring_service=monitoring_service,
        project_mcp_tool_boundary=project_mcp_tool_boundary,
        claude_supervisor=claude_supervisor,
        scheduler=scheduler,
    )


__all__ = [
    "RuntimeComposition",
    "build_runtime_composition",
]
