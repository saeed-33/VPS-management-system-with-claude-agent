from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from app.capabilities.analysis.retrieval.report_fingerprint import (
    ReportFingerprintService,
)
from app.capabilities.analysis.retrieval.report_normalizer import (
    ReportNormalizer,
)
from app.interfaces.mcp.schemas import (
    ProjectToolCall,
    ProjectToolDefinition,
    ProjectToolResult,
)
from app.interfaces.mcp.catalog import group_definitions
from app.interfaces.mcp.handlers import (
    AnalysisToolsMixin,
    BoundaryCommonMixin,
    BoundaryDefinitionsMixin,
    InvestigationToolsMixin,
    MonitoringToolsMixin,
    RemediationToolsMixin,
)


ToolHandler = Callable[
    [dict[str, Any]],
    Awaitable[ProjectToolResult],
]


class ProjectMcpToolBoundary(
    MonitoringToolsMixin,
    AnalysisToolsMixin,
    InvestigationToolsMixin,
    RemediationToolsMixin,
    BoundaryCommonMixin,
    BoundaryDefinitionsMixin,
):
    # Canonical Claude-visible project tool registry.

    def __init__(
        self,
        *,
        server_service,
        monitoring_profile_service,
        monitoring_service,
        report_query_service,
        analysis_orchestrator=None,
        analysis_repository=None,
        incident_retriever=None,
        knowledge_retriever=None,
        investigation_router=None,
        investigation_persistence_service=None,
        investigation_read_service=None,
        specialist_registry=None,
        specialist_investigation_loop=None,
        specialist_execution_service=None,
        remediation_service=None,
    ) -> None:
        self._server_service = server_service
        self._monitoring_profile_service = (
            monitoring_profile_service
        )
        self._monitoring_service = monitoring_service
        self._report_query_service = (
            report_query_service
        )
        self._analysis_orchestrator = (
            analysis_orchestrator
        )
        self._analysis_repository = (
            analysis_repository
        )
        self._incident_retriever = (
            incident_retriever
        )
        self._knowledge_retriever = (
            knowledge_retriever
        )
        self._investigation_router = (
            investigation_router
        )
        self._investigation_persistence_service = (
            investigation_persistence_service
        )
        self._investigation_read_service = (
            investigation_read_service
        )
        self._specialist_registry = (
            specialist_registry
        )
        self._specialist_investigation_loop = (
            specialist_investigation_loop
        )
        self._specialist_execution_service = (
            specialist_execution_service
        )
        self._remediation_service = (
            remediation_service
        )
        self._normalizer = ReportNormalizer()
        self._fingerprint_service = (
            ReportFingerprintService()
        )

        self._definitions = {
            item.tool_id: item
            for item in self._build_definitions()
        }

        self._handlers: dict[
            str,
            ToolHandler,
        ] = {
            "get_server_context": self._get_server_context,
            "get_monitoring_profile": self._get_monitoring_profile,
            "run_monitoring": self._run_monitoring,
            "get_report": self._get_report,
            "get_latest_report": self._get_latest_report,
            "find_exact_report_match": self._find_exact_report_match,
            "search_similar_incidents": self._search_similar_incidents,
            "get_top_similar_reports": self._get_top_similar_reports,
            "analyze_report": self._analyze_report,
            "get_analysis": self._get_analysis,
            "search_knowledge": self._search_knowledge,
            "start_investigation": self._start_investigation,
            "get_investigation": self._get_investigation,
            "get_investigation_status": self._get_investigation_status,
            "get_evidence": self._get_evidence,
            "get_available_specialists": self._get_available_specialists,
            "get_specialist_definition": self._get_specialist_definition,
            "run_specialist": self._run_specialist,
            "propose_remediation": self._propose_remediation,
            "create_remediation_plan": self._create_remediation_plan,
            "test_remediation_in_sandbox": self._test_remediation_in_sandbox,
            "get_sandbox_result": self._get_sandbox_result,
            "request_user_approval": self._request_user_approval,
            "apply_approved_remediation": self._apply_approved_remediation,
        }

    def list_tools(
        self,
    ) -> list[ProjectToolDefinition]:
        return [
            self._definitions[key]
            for key in sorted(
                self._definitions
            )
        ]

    def list_tool_groups(
        self,
    ) -> dict[str, list[ProjectToolDefinition]]:
        return group_definitions(
            self.list_tools()
        )

    async def execute(
        self,
        call: ProjectToolCall,
    ) -> ProjectToolResult:
        handler = self._handlers.get(
            call.tool_id
        )

        if handler is None:
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=False,
                error_code="unknown_tool",
                error_message=(
                    "Unknown project tool: "
                    f"{call.tool_id}"
                ),
            )

        try:
            return await handler(
                call.arguments
            )
        except ValueError as exc:
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=False,
                error_code="validation_error",
                error_message=str(exc),
            )
        except Exception as exc:
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=False,
                error_code="tool_execution_error",
                error_message=str(exc),
            )
