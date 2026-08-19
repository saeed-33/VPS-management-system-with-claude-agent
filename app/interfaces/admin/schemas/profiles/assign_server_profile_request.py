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


class AssignServerProfileRequest(BaseModel):
    """
    يمثل طلب إسناد ملف مراقبة إلى سيرفر.
    """
    profile_id: int | None

