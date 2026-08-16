"""عقود تقرير المراقبة ونتائج الفحوص التي يحتويها."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class MonitoringReportStatus(StrEnum):
    """
    الحالات التي تصف نتيجة اتصال المراقبة وتنفيذ فحوصها.

    لا يمثل هذا التعداد تشخيص العطل؛ فهو يصف فقط هل اكتملت القياسات أو فشل
    الاتصال أو انتهى التنفيذ بنتيجة جزئية أو فشل عام.
    """
    SUCCESS = "success"
    PARTIAL_FAILURE = "partial_failure"
    CONNECTION_FAILED = "connection_failed"
    FAILED = "failed"


@dataclass(slots=True)
class CommandExecutionData:
    """
    نتيجة تشغيل فحص واحد داخل دورة المراقبة.

    تحفظ البيانات النص المنفذ ومخرجاته ووقته وحالته وبصمته حتى يستطيع التحليل
    الرجوع إلى القياس الأصلي بدل الاعتماد على ملخص مجرد.
    """
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

    fingerprint_strategy: str
    fingerprint_config: dict


@dataclass(slots=True)
class MonitoringReportData:
    """
    الصورة المجمعة لحالة السيرفر أثناء دورة مراقبة واحدة.

    يجمع العقد حالة الاتصال وعدد الفحوص الناجحة والفاشلة ومدتها ونتائج الفحوص،
    ويشكل المصدر الذي يبدأ منه التحليل اللاحق.
    """
    server_id: int
    status: MonitoringReportStatus

    started_at: datetime
    finished_at: datetime
    duration_ms: float

    connection_successful: bool
    error_message: str | None

    commands_total: int
    commands_succeeded: int
    commands_failed: int

    executions: list[CommandExecutionData] = field(
        default_factory=list
    )


@dataclass(slots=True, frozen=True)
class CommandExecutionDTO:
    """
    نتيجة فحص محفوظة في قاعدة البيانات مع معرف سجلها.

    يستخدمها الاستعلام والعرض والتحليل لاستعادة المخرج الكامل للفحص داخل
    التقرير الذي احتواه.
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

    fingerprint_strategy: str
    fingerprint_config: dict


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


@dataclass(slots=True, frozen=True)
class ReportDetailsDTO:
    """
    العرض الكامل لتقرير مراقبة واحد مع بيانات السيرفر ونتائج فحوصه.

    يتيح هذا العقد قراءة القياسات التي سيعتمد عليها التحليل أو مراجعتها من
    واجهة الإدارة مع الحفاظ على رسالة الخطأ والمدة والعدادات.
    """
    id: int
    server_id: int
    monitoring_profile_id: int | None
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

    executions: list[CommandExecutionDTO] = field(
        default_factory=list
    )
