"""Contract class extracted from reports.py during the structure refactor."""

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from .command_execution_data import CommandExecutionData

from .monitoring_report_status import MonitoringReportStatus

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
