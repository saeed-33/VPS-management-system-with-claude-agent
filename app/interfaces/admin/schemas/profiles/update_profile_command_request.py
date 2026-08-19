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


class UpdateProfileCommandRequest(BaseModel):
    """
    يمثل تعديلات ترتيب أو تفعيل أمر داخل ملف مراقبة.
    """
    execution_order: int | None = Field(
        default=None,
        ge=1,
    )

    enabled: bool | None = None
    custom_timeout_seconds: float | None = None

