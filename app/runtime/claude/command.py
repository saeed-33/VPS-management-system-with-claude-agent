"""Validated native Claude CLI process command contract."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from app.runtime.claude.models import ClaudeRuntimeRequest


@dataclass(slots=True, frozen=True)
class ClaudeProcessCommand:
    argv: tuple[str, ...]
    cwd: Path | None = None
    env: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.argv:
            raise ValueError("Claude process argv must not be empty.")

        for item in self.argv:
            if not isinstance(item, str) or not item:
                raise ValueError(
                    "Claude process argv entries must be non-empty strings."
                )

        if self.cwd is not None:
            object.__setattr__(self, "cwd", Path(self.cwd).resolve())


class ClaudeProcessCommandBuilder(Protocol):
    def build(self, request: ClaudeRuntimeRequest) -> ClaudeProcessCommand:
        """Build one process command without executing it."""
