from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.runtime.claude.job_service import (
    ClaudeAgentJobService,
)
from app.runtime.claude.models import (
    ClaudeJobStatus,
    ClaudeRuntimeRequest,
    ClaudeRuntimeResult,
    ClaudeStructuredOutput,
)
from app.mcp.schemas import (
    ProjectToolCall,
    ProjectToolResult,
)


MONITORING_CYCLE_TOOL_IDS = (
    "get_server_context",
    "get_monitoring_profile",
    "run_monitoring",
    "get_latest_report",
)


@dataclass(slots=True, frozen=True)
class ClaudeMonitoringCycleResult:
    job_id: str
    status: ClaudeJobStatus
    server_id: int
    report_id: int | None
    tool_results: tuple[
        ProjectToolResult,
        ...,
    ]
    error_code: str | None = None
    error_message: str | None = None


class ClaudeSupervisedMonitoringCycle:
    def __init__(
        self,
        *,
        tool_boundary,
        agent_job_service: ClaudeAgentJobService,
    ) -> None:
        self._tool_boundary = tool_boundary
        self._agent_job_service = agent_job_service

    async def run(
        self,
        *,
        server_id: int,
        job_id: str | None = None,
    ) -> ClaudeMonitoringCycleResult:
        if server_id < 1:
            raise ValueError(
                "server_id must be >= 1."
            )

        effective_job_id = (
            job_id
            if job_id is not None
            else str(uuid4())
        )

        request = ClaudeRuntimeRequest(
            job_id=effective_job_id,
            job_type=(
                "claude_supervised_monitoring_cycle"
            ),
            prompt=(
                "Supervise one fixed monitoring cycle "
                "through controlled project tools."
            ),
            context={
                "server_id": server_id,
                "fixed_workflow_step": (
                    "periodic monitoring"
                ),
            },
            max_turns=4,
            allowed_tools=(
                MONITORING_CYCLE_TOOL_IDS
            ),
            metadata={
                "orchestration": "claude",
                "execution_mode": (
                    "project_tool_boundary"
                ),
            },
        )

        self._agent_job_service.create_from_request(
            request,
            server_id=server_id,
        )
        self._agent_job_service.mark_running(
            job_id=effective_job_id,
            session_id=(
                "claude-supervised-monitoring:"
                f"{effective_job_id}"
            ),
        )

        tool_results: list[
            ProjectToolResult
        ] = []

        server_context = await self._call_tool(
            "get_server_context",
            {
                "server_id": server_id,
            },
            tool_results,
        )

        if not server_context.success:
            return self._complete_failed(
                request=request,
                server_id=server_id,
                tool_results=tool_results,
                failed_tool=server_context,
            )

        profile_id = (
            server_context.data
            .get("server", {})
            .get("monitoring_profile_id")
        )

        if not isinstance(profile_id, int):
            failure = ProjectToolResult(
                tool_id="get_monitoring_profile",
                success=False,
                error_code="missing_profile",
                error_message=(
                    "Server has no monitoring profile."
                ),
            )
            tool_results.append(
                failure
            )
            return self._complete_failed(
                request=request,
                server_id=server_id,
                tool_results=tool_results,
                failed_tool=failure,
            )

        profile_result = await self._call_tool(
            "get_monitoring_profile",
            {
                "profile_id": profile_id,
            },
            tool_results,
        )

        if not profile_result.success:
            return self._complete_failed(
                request=request,
                server_id=server_id,
                tool_results=tool_results,
                failed_tool=profile_result,
            )

        monitoring_result = await self._call_tool(
            "run_monitoring",
            {
                "server_id": server_id,
            },
            tool_results,
        )

        if not monitoring_result.success:
            return self._complete_failed(
                request=request,
                server_id=server_id,
                tool_results=tool_results,
                failed_tool=monitoring_result,
            )

        latest_result = await self._call_tool(
            "get_latest_report",
            {
                "server_id": server_id,
            },
            tool_results,
        )

        if not latest_result.success:
            return self._complete_failed(
                request=request,
                server_id=server_id,
                tool_results=tool_results,
                failed_tool=latest_result,
            )

        report_id = (
            latest_result.data
            .get("report", {})
            .get("id")
        )

        if not isinstance(report_id, int):
            failure = ProjectToolResult(
                tool_id="get_latest_report",
                success=False,
                error_code="invalid_report_result",
                error_message=(
                    "Latest report result did not "
                    "include a report id."
                ),
            )
            tool_results.append(
                failure
            )
            return self._complete_failed(
                request=request,
                server_id=server_id,
                tool_results=tool_results,
                failed_tool=failure,
            )

        result = ClaudeMonitoringCycleResult(
            job_id=effective_job_id,
            status=ClaudeJobStatus.COMPLETED,
            server_id=server_id,
            report_id=report_id,
            tool_results=tuple(
                tool_results
            ),
        )

        self._agent_job_service.complete_from_result(
            self._runtime_result(
                request=request,
                status=ClaudeJobStatus.COMPLETED,
                summary=(
                    "Claude-supervised monitoring "
                    "cycle completed."
                ),
                report_id=report_id,
                tool_results=tool_results,
            )
        )

        return result

    async def _call_tool(
        self,
        tool_id: str,
        arguments: dict,
        tool_results: list[ProjectToolResult],
    ) -> ProjectToolResult:
        result = await self._tool_boundary.execute(
            ProjectToolCall(
                tool_id=tool_id,
                arguments=arguments,
            )
        )
        tool_results.append(
            result
        )
        return result

    def _complete_failed(
        self,
        *,
        request: ClaudeRuntimeRequest,
        server_id: int,
        tool_results: list[ProjectToolResult],
        failed_tool: ProjectToolResult,
    ) -> ClaudeMonitoringCycleResult:
        error_code = (
            failed_tool.error_code
            or "tool_failed"
        )
        error_message = (
            failed_tool.error_message
            or f"Tool failed: {failed_tool.tool_id}"
        )

        self._agent_job_service.complete_from_result(
            self._runtime_result(
                request=request,
                status=ClaudeJobStatus.FAILED,
                summary=error_message,
                report_id=None,
                tool_results=tool_results,
                error_code=error_code,
                error_message=error_message,
            )
        )

        return ClaudeMonitoringCycleResult(
            job_id=request.job_id,
            status=ClaudeJobStatus.FAILED,
            server_id=server_id,
            report_id=None,
            tool_results=tuple(
                tool_results
            ),
            error_code=error_code,
            error_message=error_message,
        )

    def _runtime_result(
        self,
        *,
        request: ClaudeRuntimeRequest,
        status: ClaudeJobStatus,
        summary: str,
        report_id: int | None,
        tool_results: list[ProjectToolResult],
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> ClaudeRuntimeResult:
        return ClaudeRuntimeResult(
            job_id=request.job_id,
            job_type=request.job_type,
            status=status,
            session_id=(
                "claude-supervised-monitoring:"
                f"{request.job_id}"
            ),
            structured_output=ClaudeStructuredOutput(
                status=status,
                summary=summary,
                data={
                    "server_id": (
                        request.context["server_id"]
                    ),
                    "report_id": report_id,
                    "tool_results": [
                        {
                            "tool_id": item.tool_id,
                            "success": item.success,
                            "error_code": (
                                item.error_code
                            ),
                        }
                        for item in tool_results
                    ],
                },
                metadata={
                    "orchestration": "claude",
                    "execution_mode": (
                        "project_tool_boundary"
                    ),
                },
            ),
            error_code=error_code,
            error_message=error_message,
            turn_count=1,
            tool_call_count=len(
                tool_results
            ),
            usage_metadata={
                "llm_provider": "ollama",
                "runtime": (
                    "claude_supervised_monitoring"
                ),
            },
        )
