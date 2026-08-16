"""
مخططات إدارة السيرفرات واختبار SSH.

تتحقق من طلبات إنشاء وتعديل السيرفر وتصف الاستجابة الإدارية ونتيجة اختبار
الاتصال دون تضمين منطق الاتصال داخل النماذج.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ServerCreateRequest(BaseModel):
    """
    يمثل طلب إضافة سيرفر للمراقبة.
    """
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    host: str = Field(
        min_length=1,
        max_length=255,
    )

    port: int = Field(
        default=22,
        ge=1,
        le=65535,
    )

    username: str = Field(
        min_length=1,
        max_length=100,
    )

    private_key_path: str | None = Field(
        default=None,
        max_length=500,
    )

    description: str | None = None

    monitor_enabled: bool = True

    interval_seconds: int = Field(
        default=60,
        ge=5,
    )
    monitoring_profile_id: int | None = None


class ServerUpdateRequest(BaseModel):
    """
    يمثل طلب تعديل بيانات سيرفر.
    """
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    host: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    port: int | None = Field(
        default=None,
        ge=1,
        le=65535,
    )

    username: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    private_key_path: str | None = None
    description: str | None = None
    monitor_enabled: bool | None = None

    interval_seconds: int | None = Field(
        default=None,
        ge=5,
    )


class ServerResponse(BaseModel):
    """
    يمثل السيرفر وبيانات حالته وتصنيف سلامته في API.
    """
    id: int
    name: str
    host: str
    port: int
    username: str

    private_key_path: str | None
    description: str | None

    monitor_enabled: bool
    interval_seconds: int
    status: str

    last_checked_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None
    last_report_id: int | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
    monitoring_profile_id: int | None
    safety_designation: str = "unclassified"


class SSHTestResponse(BaseModel):
    """
    يمثل نتيجة اختبار اتصال SSH الإداري.
    """
    success: bool
    message: str
    hostname: str | None = None
