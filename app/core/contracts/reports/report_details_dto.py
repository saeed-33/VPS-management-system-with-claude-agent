"""Contract class extracted from reports.py during the structure refactor."""

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from .command_execution_dto import CommandExecutionDTO

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
