from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CreateMonitoringProfileDTO:
    name: str
    description: str | None = None
    enabled: bool = True


@dataclass(slots=True, frozen=True)
class UpdateMonitoringProfileDTO:
    name: str | None = None
    description: str | None = None
    enabled: bool | None = None


@dataclass(slots=True, frozen=True)
class MonitoringProfileCommandConfig:
    id: int
    name: str
    command: str

    timeout_seconds: float
    execution_order: int

    fingerprint_strategy: str
    fingerprint_config: dict