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


class MonitoringProfileResponse(BaseModel):
    """
    يمثل ملف المراقبة كما تعرضه API.
    """
    id: int
    name: str
    description: str | None
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

