from enum import StrEnum
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class AnalysisHealthStatus(StrEnum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AnalysisSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AnalysisIssue(BaseModel):
    severity: AnalysisSeverity

    title: str = Field(
        min_length=1,
        max_length=250,
    )

    description: str = Field(
        min_length=1,
    )

    evidence: str | None = None
    recommendation: str | None = None

    model_config = ConfigDict(
        extra="forbid",
    )


class ReportAnalysisResult(BaseModel):
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


class StoredReportAnalysis(BaseModel):
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