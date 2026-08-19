"""
مخططات ملفات المراقبة وربط الأوامر والسيرفرات.

تحدد شكل طلبات إدارة الملف وإعدادات الأمر والاستجابة التي تعرض الترتيب
والتفعيل والعلاقات الإدارية.
"""
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class MonitoringProfileUpdateRequest(BaseModel):
    """
    يمثل طلب تعديل ملف مراقبة.
    """
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    description: str | None = None
    enabled: bool | None = None

