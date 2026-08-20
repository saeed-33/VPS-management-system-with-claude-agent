"""Port required to manage monitoring command definitions and assignments."""
from __future__ import annotations

from typing import Any, Protocol

from app.core.contracts.commands.create_command_dto import CreateCommandDTO
from app.core.contracts.commands.update_command_dto import UpdateCommandDTO
from app.core.contracts.commands.command_execution_config import CommandExecutionConfig


class CommandRepositoryPort(Protocol):
    """Persistence operations required by command-management capabilities."""

    def get_by_id(self, command_id: int) -> Any | None: ...

    def get_by_name(self, name: str) -> Any | None: ...

    def list_all(self) -> list[Any]: ...

    def create(self, data: CreateCommandDTO) -> Any: ...

    def update(self, command_id: int, data: UpdateCommandDTO) -> Any | None: ...

    def delete(self, command_id: int) -> bool: ...

    def assign_to_server(
        self,
        *,
        server_id: int,
        command_id: int,
        execution_order: int,
        enabled: bool = True,
        custom_timeout_seconds: float | None = None,
    ) -> Any: ...

    def remove_from_server(self, *, server_id: int, command_id: int) -> bool: ...

    def list_enabled_for_server(self, server_id: int) -> list[CommandExecutionConfig]: ...
