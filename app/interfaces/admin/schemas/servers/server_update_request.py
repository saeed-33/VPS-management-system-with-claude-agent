"""
مخططات إدارة السيرفرات واختبار SSH.

تتحقق من طلبات إنشاء وتعديل السيرفر وتصف الاستجابة الإدارية ونتيجة اختبار
الاتصال دون تضمين منطق الاتصال داخل النماذج.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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

