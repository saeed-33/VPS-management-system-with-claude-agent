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


class UpdateCommandAssignmentRequest(BaseModel):
    """
    يمثل تعديلات إعدادات ربط الأمر بالسيرفر.
    """
    execution_order: int | None = Field(
        default=None,
        ge=1,
    )

    enabled: bool | None = None

    custom_timeout_seconds: float | None = Field(
        default=None,
        gt=0,
    )

