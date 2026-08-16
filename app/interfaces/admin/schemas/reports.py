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

class PaginatedReportsResponse(BaseModel):
    """
    يمثل صفحة تقارير مع العدد والبيانات الوصفية للقائمة.
    """
    items: list[ReportListItemResponse]
    page: int
    page_size: int
    total: int

class CommandExecutionResponse(BaseModel):
    """
    يمثل نتيجة تنفيذ أمر داخل تقرير مراقبة.
    """
    id: int
    command_id: int | None
    command_name: str
    command_text: str
    execution_order: int

    success: bool
    exit_status: int | None

    stdout: str
    stderr: str
    error_message: str | None

    started_at: datetime
    finished_at: datetime
    duration_ms: float

    model_config = ConfigDict(
        from_attributes=True
    )


class ReportDetailsResponse(BaseModel):
    """
    يمثل تفاصيل التقرير وتنفيذاته وحالة الاتصال.
    """
    id: int
    server_id: int
    server_name: str
    server_host: str

    status: str

    started_at: datetime
    finished_at: datetime
    duration_ms: float

    connection_successful: bool
    error_message: str | None

    commands_total: int
    commands_succeeded: int
    commands_failed: int

    executions: list[CommandExecutionResponse]

    model_config = ConfigDict(
        from_attributes=True
    )


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


class ReportAnalysisSourcesResponse(BaseModel):
    """
    يمثل مجموعة مصادر سياق تحليل التقرير.
    """
    report_id: int
    analysis_id: int
    sources: list[ReportAnalysisSourceResponse]
