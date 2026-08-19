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


class CommandCreateRequest(BaseModel):
    """
    يمثل طلب إنشاء أمر مراقبة جديد.
    """
    name: str = Field(
        min_length=1,
        max_length=150,
    )
    fingerprint_strategy: (
        FingerprintStrategyValue
    ) = "canonical_lines"

    fingerprint_config: dict[str, Any] = Field(
        default_factory=dict
    )
    command: str = Field(
        min_length=1,
    )

    description: str | None = None

    timeout_seconds: float = Field(
        default=20,
        gt=0,
    )

    enabled: bool = True

