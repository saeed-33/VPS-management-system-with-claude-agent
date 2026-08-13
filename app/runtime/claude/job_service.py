from __future__ import annotations

from datetime import datetime, timezone

from app.runtime.claude.models import (
    ClaudeJobStatus,
    ClaudeRuntimeRequest,
    ClaudeRuntimeResult,
)
from app.infrastructure.database.repositories.agent_job_repository import (
    AgentJobRepository,
)
from app.core.contracts.agent_jobs import (
    CreateAgentJobDTO,
    UpdateAgentJobDTO,
)


class ClaudeAgentJobService:
    def __init__(
        self,
        repository: AgentJobRepository,
    ) -> None:
        self._repository = repository

    def create_from_request(
        self,
        request: ClaudeRuntimeRequest,
        *,
        server_id: int | None = None,
    ):
        return self._repository.create(
            CreateAgentJobDTO(
                job_id=request.job_id,
                job_type=request.job_type,
                server_id=server_id,
                status=(
                    ClaudeJobStatus.QUEUED.value
                ),
                metadata={
                    "context": dict(
                        request.context
                    ),
                    "max_turns": request.max_turns,
                    "allowed_tools": list(
                        request.allowed_tools
                    ),
                    **dict(
                        request.metadata
                    ),
                },
            )
        )

    def mark_running(
        self,
        *,
        job_id: str,
        session_id: str | None = None,
    ):
        return self._repository.update(
            job_id,
            UpdateAgentJobDTO(
                status=(
                    ClaudeJobStatus.RUNNING.value
                ),
                claude_session_id=session_id,
            ),
        )

    def complete_from_result(
        self,
        result: ClaudeRuntimeResult,
    ):
        return self._repository.update(
            result.job_id,
            UpdateAgentJobDTO(
                status=result.status.value,
                claude_session_id=result.session_id,
                completed_at=datetime.now(
                    timezone.utc
                ),
                error_code=result.error_code,
                error_message=result.error_message,
                turn_count=result.turn_count,
                tool_call_count=(
                    result.tool_call_count
                ),
                usage_metadata=dict(
                    result.usage_metadata
                ),
            ),
        )

    def recover_interrupted_jobs(
        self,
    ) -> int:
        return (
            self._repository
            .mark_unfinished_after_restart(
                statuses=(
                    ClaudeJobStatus.QUEUED.value,
                    ClaudeJobStatus.RUNNING.value,
                ),
                failed_status=(
                    ClaudeJobStatus.FAILED.value
                ),
                error_code=(
                    "interrupted_after_restart"
                ),
                error_message=(
                    "Claude agent job was queued or "
                    "running during application restart."
                ),
            )
        )
