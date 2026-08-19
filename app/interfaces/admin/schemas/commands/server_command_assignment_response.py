"""
مخططات أوامر المراقبة وربطها بالسيرفرات.

تصف طلبات إنشاء وتعديل الأوامر وطلبات الربط والاستجابات التي تعرض الأمر
وإعدادات تشغيله دون تنفيذ منطق الخدمة داخل المخطط.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Literal


FingerprintStrategyValue = Literal[
    "full_output",
    "status_only",
    "canonical_lines",
    "error_signature",
    "exclude_output",
]


class ServerCommandAssignmentResponse(BaseModel):
    """
    يمثل نتيجة ربط أمر مراقبة بسيرفر.
    """
    command_id: int
    name: str
    command: str
    default_timeout_seconds: float

    assignment_id: int
    execution_order: int
    enabled: bool
    custom_timeout_seconds: float | None

