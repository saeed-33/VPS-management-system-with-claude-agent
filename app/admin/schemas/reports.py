from datetime import datetime

from pydantic import BaseModel


from datetime import datetime

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