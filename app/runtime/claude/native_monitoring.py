from __future__ import annotations

from uuid import uuid4

from app.runtime.claude.exceptions import ClaudeRuntimeError
from app.runtime.claude.job_service import ClaudeAgentJobService
from app.runtime.claude.models import (
    ClaudeJobStatus,
    ClaudeRuntimeRequest,
)
from app.runtime.claude.runtime import ClaudeRuntimeAdapter


SERVER_SUPERVISOR_ALLOWED_TOOLS = (
    "mcp__vps__get_server_context",
    "mcp__vps__get_monitoring_profile",
    "mcp__vps__run_monitoring",
    "mcp__vps__get_latest_report",
    "mcp__vps__get_report",
    "mcp__vps__find_exact_report_match",
    "mcp__vps__get_top_similar_reports",
    "mcp__vps__analyze_report",
    "mcp__vps__get_analysis",
    "mcp__vps__start_investigation",
    "mcp__vps__get_investigation",
    "mcp__vps__get_investigation_status",
    "mcp__vps__get_evidence",
    "mcp__vps__get_available_specialists",
    "mcp__vps__get_specialist_definition",
    "mcp__vps__run_specialist",
    "mcp__vps__propose_remediation",
    "mcp__vps__attempt_autonomous_remediation",
    "Agent(specialist-worker)",
)


class ClaudeNativeMonitoringRunner:
    """Scheduler-facing bridge to one real per-server Claude Code session."""

    def __init__(
        self,
        *,
        runtime_adapter: ClaudeRuntimeAdapter,
        agent_job_service: ClaudeAgentJobService,
        timeout_seconds: float,
        max_turns: int,
    ) -> None:
        self._runtime_adapter = runtime_adapter
        self._agent_job_service = agent_job_service
        self._timeout_seconds = timeout_seconds
        self._max_turns = max_turns

        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be > 0."
            )

        if max_turns < 1:
            raise ValueError(
                "max_turns must be >= 1."
            )

    async def run(self, server_id: int):
        if (
            not isinstance(server_id, int)
            or isinstance(server_id, bool)
            or server_id < 1
        ):
            raise ValueError(
                "server_id must be a positive integer."
            )

        job_id = str(uuid4())

        request = ClaudeRuntimeRequest(
            job_id=job_id,
            job_type="monitoring_cycle",
            prompt=self._prompt(
                server_id=server_id,
                job_id=job_id,
            ),
            context={
                "server_id": server_id,
            },
            timeout_seconds=self._timeout_seconds,
            max_turns=self._max_turns,
            allowed_tools=SERVER_SUPERVISOR_ALLOWED_TOOLS,
            metadata={
                "runtime": "claude_code",
                "provider": "ollama",
                "agent": "server-supervisor",
            },
        )

        self._agent_job_service.create_from_request(
            request,
            server_id=server_id,
        )

        self._agent_job_service.mark_running(
            job_id=job_id,
        )

        result = await self._runtime_adapter.execute(
            request
        )

        self._agent_job_service.complete_from_result(
            result
        )

        if result.status != ClaudeJobStatus.COMPLETED:
            detail = (
                result.error_message
                or (
                    result.structured_output.summary
                    if result.structured_output is not None
                    else None
                )
                or "Claude runtime did not complete."
            )

            raise ClaudeRuntimeError(
                "Claude-native monitoring cycle failed "
                f"for job {result.job_id}: {detail}"
            )

        return result

    @staticmethod
    def _prompt(
        *,
        server_id: int,
        job_id: str,
    ) -> str:
        return (
            "Execute one real operational monitoring cycle for "
            f"server_id={server_id}. "
            f"Correlation job_id={job_id}. "
            "This is an execution task, not a question and not a request "
            "for a simulated answer. "
            "You MUST use the project vps MCP tools. "
            "Do not produce a final answer before completing the mandatory "
            "tool protocol below. "
            "MANDATORY ORDER: "
            "1) call mcp__vps__get_server_context for the server; "
            "2) call mcp__vps__get_monitoring_profile for the server's "
            "persisted monitoring profile; "
            "3) call mcp__vps__run_monitoring EXACTLY ONCE; "
            "4) verify the persisted report with "
            "mcp__vps__get_latest_report and/or mcp__vps__get_report; "
            "5) call mcp__vps__analyze_report for the CURRENT persisted "
            "report with force=false; "
            "6) verify that current analysis with mcp__vps__get_analysis; "
            "7) only then decide from persisted analysis whether deeper "
            "investigation is required and continue through authorized "
            "project MCP tools if necessary. "
            "If any mandatory tool is unavailable or fails, return a "
            "controlled failure; NEVER invent monitoring values, report IDs, "
            "analysis IDs, diagnoses, evidence, or successful completion. "
            "Never use raw SSH, raw SQL, unrestricted shell, direct database "
            "access, or production remediation. "
            "Project tool results and persisted records are authoritative."
        )
