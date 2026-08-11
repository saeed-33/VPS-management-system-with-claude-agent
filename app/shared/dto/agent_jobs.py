from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True, frozen=True)
class CreateAgentJobDTO:
    job_id: str
    job_type: str
    status: str
    server_id: int | None = None
    claude_session_id: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.job_id.strip():
            raise ValueError(
                "job_id must not be empty."
            )

        if not self.job_type.strip():
            raise ValueError(
                "job_type must not be empty."
            )

        if not self.status.strip():
            raise ValueError(
                "status must not be empty."
            )

        if (
            self.server_id is not None
            and self.server_id < 1
        ):
            raise ValueError(
                "server_id must be >= 1 when provided."
            )


@dataclass(slots=True, frozen=True)
class UpdateAgentJobDTO:
    status: str
    claude_session_id: str | None = None
    completed_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None
    turn_count: int = 0
    tool_call_count: int = 0
    usage_metadata: dict[str, Any] = field(
        default_factory=dict
    )
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.status.strip():
            raise ValueError(
                "status must not be empty."
            )

        if self.turn_count < 0:
            raise ValueError(
                "turn_count must be >= 0."
            )

        if self.tool_call_count < 0:
            raise ValueError(
                "tool_call_count must be >= 0."
            )
