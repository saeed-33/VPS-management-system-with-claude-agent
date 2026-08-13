class ApplicationError(Exception):
    """Base exception for application errors."""


class EntityNotFoundError(ApplicationError):
    """Raised when a database entity is not found."""


class ServerNotFoundError(EntityNotFoundError):
    def __init__(self, server_id: int) -> None:
        super().__init__(
            f"Server with id {server_id} was not found."
        )


class CommandNotFoundError(EntityNotFoundError):
    def __init__(self, command_id: int) -> None:
        super().__init__(
            f"Monitoring command with id "
            f"{command_id} was not found."
        )


class ReportNotFoundError(EntityNotFoundError):
    def __init__(self, report_id: int) -> None:
        super().__init__(
            f"Monitoring report with id "
            f"{report_id} was not found."
        )


class DuplicateEntityError(ApplicationError):
    """Raised when an entity already exists."""


class DuplicateServerError(DuplicateEntityError):
    def __init__(self, name: str) -> None:
        super().__init__(
            f"A server named '{name}' already exists."
        )


class DuplicateCommandError(DuplicateEntityError):
    def __init__(self, name: str) -> None:
        super().__init__(
            f"A monitoring command named "
            f"'{name}' already exists."
        )


class InvalidOperationError(ApplicationError):
    """Raised when an operation cannot be performed."""


class CommandAlreadyAssignedError(
    InvalidOperationError
):
    def __init__(
        self,
        server_id: int,
        command_id: int,
    ) -> None:
        super().__init__(
            f"Command {command_id} is already assigned "
            f"to server {server_id}."
        )
class MonitoringProfileNotFoundError(
    EntityNotFoundError
):
    def __init__(self, profile_id: int) -> None:
        super().__init__(
            f"Monitoring profile with id "
            f"{profile_id} was not found."
        )


class DuplicateMonitoringProfileError(
    DuplicateEntityError
):
    def __init__(self, name: str) -> None:
        super().__init__(
            f"A monitoring profile named "
            f"'{name}' already exists."
        )


class ProfileCommandNotFoundError(
    EntityNotFoundError
):
    def __init__(
        self,
        profile_id: int,
        command_id: int,
    ) -> None:
        super().__init__(
            f"Command {command_id} is not assigned "
            f"to monitoring profile {profile_id}."
        )

class SpecialistDefinitionNotFoundError(
    EntityNotFoundError
):
    def __init__(self, specialist_id: int) -> None:
        super().__init__(
            f"Specialist definition with id "
            f"{specialist_id} was not found."
        )


class DuplicateSpecialistDefinitionError(
    DuplicateEntityError
):
    def __init__(self, slug: str) -> None:
        super().__init__(
            f"A specialist with slug '{slug}' already exists."
        )
