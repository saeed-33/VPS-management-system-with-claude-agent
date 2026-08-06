from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CreateCommandDTO:
    name: str
    command: str
    fingerprint_strategy: str = "full_output"
    fingerprint_config: dict = field(
        default_factory=dict
    )
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
    fingerprint_strategy: str | None = None
    fingerprint_config: dict | None = None


@dataclass(slots=True, frozen=True)
class CommandExecutionConfig:
    id: int
    name: str
    command: str

    timeout_seconds: float
    execution_order: int