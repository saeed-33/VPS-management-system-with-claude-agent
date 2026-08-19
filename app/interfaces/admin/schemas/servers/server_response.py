"""
مخططات إدارة السيرفرات واختبار SSH.

تتحقق من طلبات إنشاء وتعديل السيرفر وتصف الاستجابة الإدارية ونتيجة اختبار
الاتصال دون تضمين منطق الاتصال داخل النماذج.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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

