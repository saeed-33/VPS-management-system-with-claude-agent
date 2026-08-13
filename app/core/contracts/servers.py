from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CreateServerDTO:
    name: str
    host: str
    port: int
    username: str

    private_key_path: str | None = None
    description: str | None = None

    monitor_enabled: bool = True
    interval_seconds: int = 60
    monitoring_profile_id: int | None = None


@dataclass(slots=True, frozen=True)
class UpdateServerDTO:
    name: str | None = None
    host: str | None = None
    port: int | None = None
    username: str | None = None

    private_key_path: str | None = None
    description: str | None = None

    monitor_enabled: bool | None = None
    interval_seconds: int | None = None
    monitoring_profile_id: int | None = None