from app.shared.database.models.monitor_command import (
    MonitorCommandModel,
)
from app.shared.database.models.monitoring_profile import (
    MonitoringProfileModel,
)
from app.shared.database.models.profile_command import (
    MonitoringProfileCommandModel,
)
from app.shared.database.models.server import (
    ServerModel,
)
from app.shared.database.repositories.command_repository import (
    CommandRepository,
)
from app.shared.database.repositories.profile_repository import (
    MonitoringProfileRepository,
)
from app.shared.database.repositories.server_repository import (
    ServerRepository,
)
from app.shared.dto.profiles import (
    CreateMonitoringProfileDTO,
    UpdateMonitoringProfileDTO,
)
from app.shared.exceptions import (
    CommandNotFoundError,
    DuplicateMonitoringProfileError,
    MonitoringProfileNotFoundError,
    ProfileCommandNotFoundError,
    ServerNotFoundError,
)


class MonitoringProfileService:
    def __init__(
        self,
        *,
        profile_repository: MonitoringProfileRepository,
        command_repository: CommandRepository,
        server_repository: ServerRepository,
    ) -> None:
        self._profile_repository = profile_repository
        self._command_repository = command_repository
        self._server_repository = server_repository

    def list_profiles(
        self,
    ) -> list[MonitoringProfileModel]:
        return self._profile_repository.list_all()

    def get_profile(
        self,
        profile_id: int,
    ) -> MonitoringProfileModel:
        profile = self._profile_repository.get_by_id(
            profile_id
        )

        if profile is None:
            raise MonitoringProfileNotFoundError(
                profile_id
            )

        return profile

    def create_profile(
        self,
        data: CreateMonitoringProfileDTO,
    ) -> MonitoringProfileModel:
        if not data.name.strip():
            raise ValueError(
                "Monitoring profile name is required."
            )

        existing = self._profile_repository.get_by_name(
            data.name.strip()
        )

        if existing is not None:
            raise DuplicateMonitoringProfileError(
                data.name
            )

        return self._profile_repository.create(data)

    def update_profile(
        self,
        profile_id: int,
        data: UpdateMonitoringProfileDTO,
    ) -> MonitoringProfileModel:
        current = self.get_profile(profile_id)

        if (
            data.name is not None
            and data.name.strip() != current.name
        ):
            duplicate = (
                self._profile_repository.get_by_name(
                    data.name.strip()
                )
            )

            if duplicate is not None:
                raise DuplicateMonitoringProfileError(
                    data.name
                )

        updated = self._profile_repository.update(
            profile_id,
            data,
        )

        if updated is None:
            raise MonitoringProfileNotFoundError(
                profile_id
            )

        return updated

    def delete_profile(
        self,
        profile_id: int,
    ) -> None:
        deleted = self._profile_repository.delete(
            profile_id
        )

        if not deleted:
            raise MonitoringProfileNotFoundError(
                profile_id
            )

    def list_profile_commands(
        self,
        profile_id: int,
    ) -> list[
        tuple[
            MonitorCommandModel,
            MonitoringProfileCommandModel,
        ]
    ]:
        self.get_profile(profile_id)

        return (
            self._profile_repository
            .list_profile_commands(profile_id)
        )

    def assign_command(
        self,
        *,
        profile_id: int,
        command_id: int,
        execution_order: int,
        enabled: bool,
        custom_timeout_seconds: float | None,
    ) -> MonitoringProfileCommandModel:
        self.get_profile(profile_id)

        command = self._command_repository.get_by_id(
            command_id
        )

        if command is None:
            raise CommandNotFoundError(command_id)

        if execution_order < 1:
            raise ValueError(
                "Execution order must be greater "
                "than zero."
            )

        return self._profile_repository.assign_command(
            profile_id=profile_id,
            command_id=command_id,
            execution_order=execution_order,
            enabled=enabled,
            custom_timeout_seconds=(
                custom_timeout_seconds
            ),
        )

    def update_command_assignment(
        self,
        *,
        profile_id: int,
        command_id: int,
        execution_order: int | None,
        enabled: bool | None,
        custom_timeout_seconds: float | None,
        update_custom_timeout: bool,
    ) -> MonitoringProfileCommandModel:
        self.get_profile(profile_id)

        updated = (
            self._profile_repository
            .update_command_assignment(
                profile_id=profile_id,
                command_id=command_id,
                execution_order=execution_order,
                enabled=enabled,
                custom_timeout_seconds=(
                    custom_timeout_seconds
                ),
                update_custom_timeout=(
                    update_custom_timeout
                ),
            )
        )

        if updated is None:
            raise ProfileCommandNotFoundError(
                profile_id,
                command_id,
            )

        return updated

    def remove_command(
        self,
        *,
        profile_id: int,
        command_id: int,
    ) -> None:
        removed = (
            self._profile_repository.remove_command(
                profile_id=profile_id,
                command_id=command_id,
            )
        )

        if not removed:
            raise ProfileCommandNotFoundError(
                profile_id,
                command_id,
            )

    def assign_profile_to_server(
        self,
        *,
        server_id: int,
        profile_id: int | None,
    ) -> ServerModel:
        if (
            self._server_repository.get_by_id(server_id)
            is None
        ):
            raise ServerNotFoundError(server_id)

        if profile_id is not None:
            self.get_profile(profile_id)

        server = (
            self._profile_repository
            .assign_profile_to_server(
                server_id=server_id,
                profile_id=profile_id,
            )
        )

        if server is None:
            raise ServerNotFoundError(server_id)

        return server