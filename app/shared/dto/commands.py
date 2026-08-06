from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CreateCommandDTO:
    name: str
    command: str

    description: str | None = None
    timeout_seconds: float = 20.0
    enabled: bool = True


@dataclass(slots=True, frozen=True)
class UpdateCommandDTO:
    name: str | None = None
    command: str | None = None

    description: str | None = None
    timeout_seconds: float | None = None
    enabled: bool | None = None


@dataclass(slots=True, frozen=True)
class CommandExecutionConfig:
    id: int
    name: str
    command: str

    timeout_seconds: float
    execution_order: int