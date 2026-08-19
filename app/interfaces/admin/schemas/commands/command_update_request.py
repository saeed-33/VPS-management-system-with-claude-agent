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


class CommandUpdateRequest(BaseModel):
    """
    يمثل طلب تعديل أمر مراقبة موجود.
    """
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    command: str | None = Field(
        default=None,
        min_length=1,
    )

    description: str | None = None

    timeout_seconds: float | None = Field(
        default=None,
        gt=0,
    )

    enabled: bool | None = None

    fingerprint_strategy: FingerprintStrategyValue | None = None
    fingerprint_config: dict[str, Any] | None = None

