from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class MonitoringReportStatus(StrEnum):
    SUCCESS = "success"
    PARTIAL_FAILURE = "partial_failure"
    CONNECTION_FAILED = "connection_failed"
    FAILED = "failed"


@dataclass(slots=True)
class CommandExecutionData:
    command_id: int | None
    command_name: str
    command_text: str
    execution_order: int

    success: bool
    exit_status: int | None

    stdout: str
    stderr: str
    error_message: str | None

    started_at: datetime
    finished_at: datetime
    duration_ms: float

    fingerprint_strategy: str
    fingerprint_config: dict


@dataclass(slots=True)
class MonitoringReportData:
    server_id: int
    status: MonitoringReportStatus

    started_at: datetime
    finished_at: datetime
    duration_ms: float

    connection_successful: bool
    error_message: str | None

    commands_total: int
    commands_succeeded: int
    commands_failed: int

    executions: list[CommandExecutionData] = field(
        default_factory=list
    )


@dataclass(slots=True, frozen=True)
class CommandExecutionDTO:
    id: int
    command_id: int | None

    command_name: str
    command_text: str
    execution_order: int

    success: bool
    exit_status: int | None

    stdout: str
    stderr: str
    error_message: str | None

    started_at: datetime
    finished_at: datetime
    duration_ms: float

    fingerprint_strategy: str
    fingerprint_config: dict


@dataclass(slots=True, frozen=True)
class ReportListItemDTO:
    id: int
    server_id: int
    server_name: str

    status: str

    started_at: datetime
    finished_at: datetime
    duration_ms: float

    connection_successful: bool

    commands_total: int
    commands_succeeded: int
    commands_failed: int


@dataclass(slots=True, frozen=True)
class ReportDetailsDTO:
    id: int
    server_id: int
    monitoring_profile_id: int | None
    server_name: str
    server_host: str
    status: str

    started_at: datetime
    finished_at: datetime
    duration_ms: float

    connection_successful: bool
    error_message: str | None

    commands_total: int
    commands_succeeded: int
    commands_failed: int

    executions: list[CommandExecutionDTO] = field(
        default_factory=list
    )