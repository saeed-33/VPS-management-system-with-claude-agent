"""
مخططات تقارير المراقبة وتحليلاتها.

تحدد شكل عناصر القائمة والتفاصيل والتنفيذات ونتائج التحليل ومصادر السياق التي
تعرضها واجهة الإدارة.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReportAnalysisSourcesResponse(BaseModel):
    """
    يمثل مجموعة مصادر سياق تحليل التقرير.
    """
    report_id: int
    analysis_id: int
    sources: list[ReportAnalysisSourceResponse]

