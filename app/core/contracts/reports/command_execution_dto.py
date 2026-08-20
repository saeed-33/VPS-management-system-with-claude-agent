"""Contract class extracted from reports.py during the structure refactor."""

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

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
