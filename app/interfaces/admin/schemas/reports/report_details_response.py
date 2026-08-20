"""
مخططات تقارير المراقبة وتحليلاتها.

تحدد شكل عناصر القائمة والتفاصيل والتنفيذات ونتائج التحليل ومصادر السياق التي
تعرضها واجهة الإدارة.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReportDetailsResponse(BaseModel):
    """
    يمثل تفاصيل التقرير وتنفيذاته وحالة الاتصال.
    """
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

