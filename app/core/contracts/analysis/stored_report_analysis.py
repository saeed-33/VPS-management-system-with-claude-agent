"""Contract class extracted from analysis.py during the structure refactor."""

from enum import StrEnum

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from .analysis_health_status import AnalysisHealthStatus

from .analysis_issue import AnalysisIssue

class StoredReportAnalysis(BaseModel):
    """
    تحليل محفوظ مرتبط بتقرير وسيرفر ومزود النموذج الذي أنتجه.

    يحافظ على الحالة والملخص والأخطاء والأزمنة وعدد المحاولات حتى يمكن إعادة
    استخدام تحليل مطابق أو معرفة لماذا لم يكتمل.
    """
    id: int
    report_id: int
    server_id: int

    provider_name: str
    model_name: str
    status: str

    health_status: AnalysisHealthStatus | None
    summary: str | None

    issues: list[AnalysisIssue] = Field(
        default_factory=list,
    )

    positive_findings: list[str] = Field(
        default_factory=list,
    )

    recommended_actions: list[str] = Field(
        default_factory=list,
    )

    analysis_error: str | None

    started_at: datetime | None
    finished_at: datetime | None
    duration_ms: float | None

    attempts: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
