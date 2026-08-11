from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class ProjectToolDefinition:
    tool_id: str
    description: str
    input_schema: dict[str, Any]
    read_only: bool = True

    def __post_init__(self) -> None:
        if not self.tool_id.strip():
            raise ValueError(
                "tool_id must not be empty."
            )

        if not self.description.strip():
            raise ValueError(
                "description must not be empty."
            )


@dataclass(slots=True, frozen=True)
class ProjectToolCall:
    tool_id: str
    arguments: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.tool_id.strip():
            raise ValueError(
                "tool_id must not be empty."
            )


@dataclass(slots=True, frozen=True)
class ProjectToolResult:
    tool_id: str
    success: bool
    data: dict[str, Any] = field(
        default_factory=dict
    )
    error_code: str | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if not self.tool_id.strip():
            raise ValueError(
                "tool_id must not be empty."
            )

        if self.success:
            if self.error_code is not None:
                raise ValueError(
                    "successful tool result cannot "
                    "have error_code."
                )
            if self.error_message is not None:
                raise ValueError(
                    "successful tool result cannot "
                    "have error_message."
                )
