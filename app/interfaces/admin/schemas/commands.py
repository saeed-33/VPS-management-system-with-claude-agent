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


class AssignCommandRequest(BaseModel):
    """
    يمثل طلب ربط أمر مراقبة بسيرفر.
    """
    execution_order: int = Field(
        default=1,
        ge=1,
    )

    enabled: bool = True

    custom_timeout_seconds: float | None = Field(
        default=None,
        gt=0,
    )


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
