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

class ReportAnalysisResult(BaseModel):
    """
    ملخص التحليل الذي يحدد صحة السيرفر وما يستحق التحقيق.

    يفصل العقد بين المشكلات والنتائج الإيجابية والأفعال المقترحة، حتى لا تختلط
    ملاحظة التقرير بتشخيص نهائي أو تغيير منفذ.
    """
    health_status: AnalysisHealthStatus

    summary: str = Field(
        min_length=1,
    )

    issues: list[AnalysisIssue] = Field(
        default_factory=list,
    )

    positive_findings: list[str] = Field(
        default_factory=list,
    )

    recommended_actions: list[str] = Field(
        default_factory=list,
    )

    model_config = ConfigDict(
        extra="forbid",
    )
