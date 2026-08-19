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

