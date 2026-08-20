"""
مخططات تقارير المراقبة وتحليلاتها.

تحدد شكل عناصر القائمة والتفاصيل والتنفيذات ونتائج التحليل ومصادر السياق التي
تعرضها واجهة الإدارة.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReportAnalysisResponse(BaseModel):
    """
    يمثل نتيجة تحليل تقرير المراقبة.
    """
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

    report_fingerprint: str | None
    analysis_source: str
    reused_from_analysis_id: int | None
    retrieval_strategy: str | None
    retrieval_score: float | None
    llm_called: bool

    model_config = ConfigDict(
        from_attributes=True
    )

