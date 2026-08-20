"""
مخططات تقارير المراقبة وتحليلاتها.

تحدد شكل عناصر القائمة والتفاصيل والتنفيذات ونتائج التحليل ومصادر السياق التي
تعرضها واجهة الإدارة.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReportAnalysisSourceResponse(BaseModel):
    """
    يمثل مصدرًا تاريخيًا أو حاليًا استخدمه التحليل.
    """
    id: int
    source_type: str

    source_report_id: int | None
    source_analysis_id: int | None

    retrieval_strategy: str | None
    similarity_score: float | None
    rank: int | None

    title: str
    excerpt: str | None
    source_metadata: dict[str, Any]

    used_in_prompt: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

