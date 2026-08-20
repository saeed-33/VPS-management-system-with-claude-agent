"""Contract class extracted from reports.py during the structure refactor."""

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

@dataclass(slots=True, frozen=True)
class ReportListItemDTO:
    """
    ملخص خفيف لتقرير مراقبة يستخدم في القوائم والبحث.

    يعرض هوية السيرفر وحالة الدورة والعدادات الأساسية دون تحميل نتائج كل
    الفحوص التفصيلية.
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
