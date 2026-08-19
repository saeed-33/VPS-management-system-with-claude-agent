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


class CommandResponse(BaseModel):
    """
    يمثل أمر مراقبة كما تعرضه API.
    """
    id: int
    name: str
    command: str
    description: str | None
    timeout_seconds: float
    enabled: bool
    created_at: datetime
    updated_at: datetime
    fingerprint_strategy: str
    fingerprint_config: dict[str, Any]
    model_config = ConfigDict(
        from_attributes=True
    )

