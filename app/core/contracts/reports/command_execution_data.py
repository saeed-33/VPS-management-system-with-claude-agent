"""Contract class extracted from reports.py during the structure refactor."""

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

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
