from __future__ import annotations

import asyncio
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


MULTI_SPECIALIST_TOOL_IDS = (
    "get_investigation",
    "get_specialist_definition",
    "run_specialist",
)


@dataclass(slots=True, frozen=True)
class ClaudeSpecialistRunSummary:
    specialist_slug: str
    task_id: str | None
    status: str | None
    confidence: float | None
    evidence_ids: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class ClaudeMultiSpecialistResult:
    job_id: str
    status: ClaudeJobStatus
    investigation_id: str
    specialist_runs: tuple[
        ClaudeSpecialistRunSummary,
        ...,
    ]
    tool_results: tuple[
        ProjectToolResult,
        ...,
    ]
    error_code: str | None = None
    error_message: str | None = None


class ClaudeMultiSpecialistSupervisor:
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
        investigation_id: str,
        objective: str,
        job_id: str | None = None,
        max_specialists: int | None = None,
        max_turns: int = 8,
        max_tool_calls: int = 12,
        timeout_seconds: float = 120.0,
    ) -> ClaudeMultiSpecialistResult:
        if not investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )
        if not objective.strip():
            raise ValueError(
                "objective must not be empty."
            )
        if max_specialists is not None and max_specialists < 1:
            raise ValueError(
                "max_specialists must be >= 1 when provided."
            )
        if max_turns < 1:
            raise ValueError(
                "max_turns must be >= 1."
            )
        if max_tool_calls < 1:
            raise ValueError(
                "max_tool_calls must be >= 1."
            )
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be > 0."
            )

        effective_job_id = (
            job_id
            if job_id is not None
            else str(uuid4())
        )
        request = ClaudeRuntimeRequest(
            job_id=effective_job_id,
            job_type=(
                "claude_multi_specialist_supervision"
            ),
            prompt=(
                "Coordinate selected DB-defined "
                "Specialists through controlled "
                "project tools."
            ),
            context={
                "investigation_id": (
                    investigation_id.strip()
                ),
                "fixed_workflow_step": (
                    "specialist deep analysis"
                ),
            },
            timeout_seconds=timeout_seconds,
            max_turns=max_turns,
            allowed_tools=MULTI_SPECIALIST_TOOL_IDS,
            metadata={
                "orchestration": "claude",
                "execution_mode": (
                    "project_tool_boundary"
                ),
                "max_specialists": max_specialists,
                "max_tool_calls": max_tool_calls,
            },
        )

        self._agent_job_service.create_from_request(
            request
        )
        self._agent_job_service.mark_running(
            job_id=effective_job_id,
            session_id=(
                "claude-multi-specialist:"
                f"{effective_job_id}"
            ),
        )

        try:
            async with asyncio.timeout(
                timeout_seconds
            ):
                return await self._run_steps(
                    request=request,
                    objective=objective.strip(),
                    max_specialists=max_specialists,
                    max_tool_calls=max_tool_calls,
                )
        except TimeoutError:
            return self._complete_failed(
                request=request,
                tool_results=[],
                specialist_runs=[],
                error_code="job_timeout",
                error_message=(
                    "Claude multi-Specialist "
                    "supervision timed out."
                ),
            )

    async def _run_steps(
        self,
        *,
        request: ClaudeRuntimeRequest,
        objective: str,
        max_specialists: int | None,
        max_tool_calls: int,
    ) -> ClaudeMultiSpecialistResult:
        tool_results: list[
            ProjectToolResult
        ] = []
        specialist_runs: list[
            ClaudeSpecialistRunSummary
        ] = []

        investigation_result = await self._call_tool(
            "get_investigation",
            {
                "investigation_id": (
                    request.context[
                        "investigation_id"
                    ]
                )
            },
            tool_results,
            max_tool_calls=max_tool_calls,
        )
        if not investigation_result.success:
            return self._complete_failed_from_tool(
                request=request,
                tool_results=tool_results,
                specialist_runs=specialist_runs,
                failed_tool=investigation_result,
            )

        investigation = (
            investigation_result
            .data
            .get("investigation", {})
        )
        selected_slugs = self._selected_slugs(
            investigation
        )
        if not selected_slugs:
            return self._complete_success(
                request=request,
                tool_results=tool_results,
                specialist_runs=specialist_runs,
                summary=(
                    "No selected Specialists were "
                    "available for supervision."
                ),
            )

        investigation_limit = (
            investigation.get("max_specialists")
        )
        if not isinstance(
            investigation_limit,
            int,
        ):
            investigation_limit = len(
                selected_slugs
            )

        effective_limit = min(
            investigation_limit,
            max_specialists
            if max_specialists is not None
            else investigation_limit,
            len(selected_slugs),
        )

        for slug in selected_slugs[:effective_limit]:
            definition_result = await self._call_tool(
                "get_specialist_definition",
                {
                    "specialist_slug": slug,
                },
                tool_results,
                max_tool_calls=max_tool_calls,
            )
            if not definition_result.success:
                return self._complete_failed_from_tool(
                    request=request,
                    tool_results=tool_results,
                    specialist_runs=specialist_runs,
                    failed_tool=definition_result,
                )

            run_result = await self._call_tool(
                "run_specialist",
                {
                    "investigation_id": (
                        request.context[
                            "investigation_id"
                        ]
                    ),
                    "specialist_slug": slug,
                    "objective": objective,
                },
                tool_results,
                max_tool_calls=max_tool_calls,
            )
            if not run_result.success:
                return self._complete_failed_from_tool(
                    request=request,
                    tool_results=tool_results,
                    specialist_runs=specialist_runs,
                    failed_tool=run_result,
                )

            specialist_runs.append(
                self._summarize_run(
                    slug,
                    run_result,
                )
            )

        return self._complete_success(
            request=request,
            tool_results=tool_results,
            specialist_runs=specialist_runs,
            summary=(
                "Claude multi-Specialist "
                "supervision completed."
            ),
        )

    async def _call_tool(
        self,
        tool_id: str,
        arguments: dict,
        tool_results: list[ProjectToolResult],
        *,
        max_tool_calls: int,
    ) -> ProjectToolResult:
        if len(tool_results) >= max_tool_calls:
            result = ProjectToolResult(
                tool_id=tool_id,
                success=False,
                error_code="tool_call_budget_exceeded",
                error_message=(
                    "Claude multi-Specialist "
                    "supervision exceeded the "
                    "configured tool call budget."
                ),
            )
            tool_results.append(
                result
            )
            return result

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

    def _complete_success(
        self,
        *,
        request: ClaudeRuntimeRequest,
        tool_results: list[ProjectToolResult],
        specialist_runs: list[
            ClaudeSpecialistRunSummary
        ],
        summary: str,
    ) -> ClaudeMultiSpecialistResult:
        self._agent_job_service.complete_from_result(
            self._runtime_result(
                request=request,
                status=ClaudeJobStatus.COMPLETED,
                summary=summary,
                tool_results=tool_results,
                specialist_runs=specialist_runs,
            )
        )

        return ClaudeMultiSpecialistResult(
            job_id=request.job_id,
            status=ClaudeJobStatus.COMPLETED,
            investigation_id=(
                request.context[
                    "investigation_id"
                ]
            ),
            specialist_runs=tuple(
                specialist_runs
            ),
            tool_results=tuple(
                tool_results
            ),
        )

    def _complete_failed_from_tool(
        self,
        *,
        request: ClaudeRuntimeRequest,
        tool_results: list[ProjectToolResult],
        specialist_runs: list[
            ClaudeSpecialistRunSummary
        ],
        failed_tool: ProjectToolResult,
    ) -> ClaudeMultiSpecialistResult:
        return self._complete_failed(
            request=request,
            tool_results=tool_results,
            specialist_runs=specialist_runs,
            error_code=(
                failed_tool.error_code
                or "tool_failed"
            ),
            error_message=(
                failed_tool.error_message
                or f"Tool failed: {failed_tool.tool_id}"
            ),
        )

    def _complete_failed(
        self,
        *,
        request: ClaudeRuntimeRequest,
        tool_results: list[ProjectToolResult],
        specialist_runs: list[
            ClaudeSpecialistRunSummary
        ],
        error_code: str,
        error_message: str,
    ) -> ClaudeMultiSpecialistResult:
        self._agent_job_service.complete_from_result(
            self._runtime_result(
                request=request,
                status=ClaudeJobStatus.FAILED,
                summary=error_message,
                tool_results=tool_results,
                specialist_runs=specialist_runs,
                error_code=error_code,
                error_message=error_message,
            )
        )

        return ClaudeMultiSpecialistResult(
            job_id=request.job_id,
            status=ClaudeJobStatus.FAILED,
            investigation_id=(
                request.context[
                    "investigation_id"
                ]
            ),
            specialist_runs=tuple(
                specialist_runs
            ),
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
        tool_results: list[ProjectToolResult],
        specialist_runs: list[
            ClaudeSpecialistRunSummary
        ],
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> ClaudeRuntimeResult:
        return ClaudeRuntimeResult(
            job_id=request.job_id,
            job_type=request.job_type,
            status=status,
            session_id=(
                "claude-multi-specialist:"
                f"{request.job_id}"
            ),
            structured_output=ClaudeStructuredOutput(
                status=status,
                summary=summary,
                data={
                    "investigation_id": (
                        request.context[
                            "investigation_id"
                        ]
                    ),
                    "specialist_runs": [
                        {
                            "specialist_slug": (
                                item.specialist_slug
                            ),
                            "task_id": item.task_id,
                            "status": item.status,
                            "confidence": (
                                item.confidence
                            ),
                            "evidence_ids": list(
                                item.evidence_ids
                            ),
                        }
                        for item in specialist_runs
                    ],
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
                    "claude_multi_specialist"
                ),
            },
        )

    @staticmethod
    def _selected_slugs(
        investigation: dict,
    ) -> tuple[str, ...]:
        candidates = investigation.get(
            "candidates",
            [],
        )
        if not isinstance(candidates, list):
            return ()

        selected = [
            item
            for item in candidates
            if isinstance(item, dict)
            and item.get("is_selected") is True
            and isinstance(
                item.get("specialist_slug"),
                str,
            )
        ]
        selected.sort(
            key=lambda item: (
                item.get("selected_rank")
                if isinstance(
                    item.get("selected_rank"),
                    int,
                )
                else 999_999,
                item["specialist_slug"],
            )
        )

        return tuple(
            item["specialist_slug"]
            for item in selected
        )

    @staticmethod
    def _summarize_run(
        specialist_slug: str,
        result: ProjectToolResult,
    ) -> ClaudeSpecialistRunSummary:
        payload = (
            result.data
            .get("result", {})
            .get("final_result", {})
        )
        if not isinstance(payload, dict):
            payload = {}

        evidence_ids = payload.get(
            "evidence_ids",
            [],
        )
        if not isinstance(evidence_ids, list):
            evidence_ids = []

        confidence = payload.get(
            "confidence"
        )
        if not isinstance(
            confidence,
            float | int,
        ):
            confidence = None

        return ClaudeSpecialistRunSummary(
            specialist_slug=specialist_slug,
            task_id=payload.get("task_id")
            if isinstance(
                payload.get("task_id"),
                str,
            )
            else None,
            status=payload.get("status")
            if isinstance(
                payload.get("status"),
                str,
            )
            else None,
            confidence=(
                float(confidence)
                if confidence is not None
                else None
            ),
            evidence_ids=tuple(
                str(item)
                for item in evidence_ids
                if isinstance(item, str)
            ),
        )
