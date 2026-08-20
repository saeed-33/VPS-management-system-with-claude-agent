"""
مخططات تقارير المراقبة وتحليلاتها.

تحدد شكل عناصر القائمة والتفاصيل والتنفيذات ونتائج التحليل ومصادر السياق التي
تعرضها واجهة الإدارة.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PaginatedReportsResponse(BaseModel):
    """
    يمثل صفحة تقارير مع العدد والبيانات الوصفية للقائمة.
    """
    items: list[ReportListItemResponse]
    page: int
    page_size: int
    total: int

