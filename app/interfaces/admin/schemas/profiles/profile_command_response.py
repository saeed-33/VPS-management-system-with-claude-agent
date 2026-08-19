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


class ProfileCommandResponse(BaseModel):
    """
    يمثل أمرًا مرتبطًا بملف مراقبة مع إعدادات الربط.
    """
    assignment_id: int
    command_id: int
    name: str
    command: str
    description: str | None
    default_timeout_seconds: float

    execution_order: int
    enabled: bool
    custom_timeout_seconds: float | None

