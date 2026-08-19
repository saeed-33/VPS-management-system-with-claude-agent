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


class MonitoringProfileCreateRequest(BaseModel):
    """
    يمثل طلب إنشاء ملف مراقبة.
    """
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None
    enabled: bool = True

