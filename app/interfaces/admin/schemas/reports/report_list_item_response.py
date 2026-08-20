"""
مخططات تقارير المراقبة وتحليلاتها.

تحدد شكل عناصر القائمة والتفاصيل والتنفيذات ونتائج التحليل ومصادر السياق التي
تعرضها واجهة الإدارة.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReportListItemResponse(BaseModel):
    """
    يمثل العنصر المختصر لتقرير مراقبة في القائمة.
    """
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

