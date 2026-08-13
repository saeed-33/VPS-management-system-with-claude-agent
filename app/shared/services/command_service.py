from app.shared.database.models.monitor_command import (
    MonitorCommandModel,
)
from app.shared.database.models.profile_command import (
    MonitoringProfileCommandModel,
)
from app.infrastructure.database.repositories.command_repository import (
    CommandRepository,
)
from app.infrastructure.database.repositories.server_repository import (
    ServerRepository,
)
from app.shared.dto.commands import (
    CreateCommandDTO,
    UpdateCommandDTO,
)
from app.shared.exceptions import (
    CommandNotFoundError,
    DuplicateCommandError,
    ServerNotFoundError,
)


class CommandService:
    def __init__(
        self,
        command_repository: CommandRepository,
        server_repository: ServerRepository,
    ) -> None:
        self._command_repository = (
            command_repository
        )
        self._server_repository = (
            server_repository
        )

    def list_commands(
        self,
    ) -> list[MonitorCommandModel]:
        return self._command_repository.list_all()

    def get_command(
        self,
        command_id: int,
    ) -> MonitorCommandModel:
        command = (
            self._command_repository.get_by_id(
                command_id
            )
        )

        if command is None:
            raise CommandNotFoundError(command_id)

        return command

    def create_command(
        self,
        data: CreateCommandDTO,
    ) -> MonitorCommandModel:
        self._validate_create(data)

        existing = (
            self._command_repository.get_by_name(
                data.name.strip()
            )
        )

        if existing is not None:
            raise DuplicateCommandError(
                data.name
            )

        return self._command_repository.create(
            data
        )

    def update_command(
        self,
        command_id: int,
        data: UpdateCommandDTO,
    ) -> MonitorCommandModel:
        existing = (
            self._command_repository.get_by_id(
                command_id
            )
        )

        if existing is None:
            raise CommandNotFoundError(command_id)

        if (
            data.name is not None
            and data.name.strip() != existing.name
        ):
            duplicate = (
                self._command_repository
                .get_by_name(data.name.strip())
            )

            if duplicate is not None:
                raise DuplicateCommandError(
                    data.name
                )

        updated = (
            self._command_repository.update(
                command_id,
                data,
            )
        )

        if updated is None:
            raise CommandNotFoundError(command_id)

        return updated

    def delete_command(
        self,
        command_id: int,
    ) -> None:
        deleted = (
            self._command_repository.delete(
                command_id
            )
        )

        if not deleted:
            raise CommandNotFoundError(command_id)

    def assign_command_to_server(
        self,
        *,
        server_id: int,
        command_id: int,
        execution_order: int,
        enabled: bool = True,
        custom_timeout_seconds: (
            float | None
        ) = None,
    ) -> MonitoringProfileCommandModel:
        if (
            self._server_repository.get_by_id(
                server_id
            )
            is None
        ):
            raise ServerNotFoundError(server_id)

        if (
            self._command_repository.get_by_id(
                command_id
            )
            is None
        ):
            raise CommandNotFoundError(command_id)

        if execution_order < 1:
            raise ValueError(
                "Execution order must be "
                "greater than zero."
            )

        if (
            custom_timeout_seconds is not None
            and custom_timeout_seconds <= 0
        ):
            raise ValueError(
                "Custom timeout must be "
                "greater than zero."
            )

        return (
            self._command_repository
            .assign_to_server(
                server_id=server_id,
                command_id=command_id,
                execution_order=execution_order,
                enabled=enabled,
                custom_timeout_seconds=(
                    custom_timeout_seconds
                ),
            )
        )

    def remove_command_from_server(
        self,
        *,
        server_id: int,
        command_id: int,
    ) -> None:
        removed = (
            self._command_repository
            .remove_from_server(
                server_id=server_id,
                command_id=command_id,
            )
        )

        if not removed:
            raise CommandNotFoundError(command_id)

    @staticmethod
    def _validate_create(
        data: CreateCommandDTO,
    ) -> None:
        if not data.name.strip():
            raise ValueError(
                "Command name is required."
            )

        if not data.command.strip():
            raise ValueError(
                "Command text is required."
            )

        if data.timeout_seconds <= 0:
            raise ValueError(
                "Command timeout must be "
                "greater than zero."
            )