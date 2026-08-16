"""عقود نتيجة تحليل تقرير المراقبة قبل بدء التحقيق المتخصص."""
from enum import StrEnum
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class AnalysisHealthStatus(StrEnum):
    """
    التقييم العام لصحة السيرفر كما ظهر من تقرير المراقبة.
    """
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AnalysisSeverity(StrEnum):
    """
    شدة ملاحظة أو مشكلة اكتشفها تحليل التقرير.
    """
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ErrorClassification(StrEnum):
    """
    تصنيف أولي لطبيعة المشكلة قبل أن يثبت التحقيق سببها.
    """
    NORMAL = "normal"
    DANGEROUS = "dangerous"
    SENSITIVE = "sensitive"


class AnalysisIssue(BaseModel):
    """
    مشكلة مستخرجة من تقرير المراقبة مع شدتها ووصفها وقرينتها الأولية.

    قد تحمل توصية مبدئية، لكنها لا تتحول إلى معالجة معتمدة قبل أن يراجعها
    التحقيق والأدلة الحالية.
    """
    severity: AnalysisSeverity
    classification: ErrorClassification | None = None

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
