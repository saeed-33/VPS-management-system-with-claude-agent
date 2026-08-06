from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReportListItemResponse(BaseModel):
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

    model_config = ConfigDict(
        from_attributes=True
    )

class PaginatedReportsResponse(BaseModel):
    items: list[ReportListItemResponse]
    page: int
    page_size: int
    total: int

class CommandExecutionResponse(BaseModel):
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

    model_config = ConfigDict(
        from_attributes=True
    )


class ReportDetailsResponse(BaseModel):
    id: int
    server_id: int
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

    executions: list[CommandExecutionResponse]

    model_config = ConfigDict(
        from_attributes=True
    )


class ReportAnalysisResponse(BaseModel):
    id: int
    report_id: int
    server_id: int

    provider_name: str
    model_name: str
    status: str

    health_status: str | None
    summary: str | None

    issues: list[dict[str, Any]]
    positive_findings: list[str]
    recommended_actions: list[str]

    analysis_error: str | None
    duration_ms: float | None
    attempts: int

    model_config = ConfigDict(
        from_attributes=True
    )