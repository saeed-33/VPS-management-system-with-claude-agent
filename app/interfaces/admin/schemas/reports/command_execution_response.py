"""
مخططات تقارير المراقبة وتحليلاتها.

تحدد شكل عناصر القائمة والتفاصيل والتنفيذات ونتائج التحليل ومصادر السياق التي
تعرضها واجهة الإدارة.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CommandExecutionResponse(BaseModel):
    """
    يمثل نتيجة تنفيذ أمر داخل تقرير مراقبة.
    """
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

