"""
مخططات تعريفات الاختصاصيين.

تحدد طلبات إنشاء وتعديل وتفعيل الاختصاصي، وتطبع المعرف والاسم قبل تمريرهما إلى
خدمة تعريفات المجال.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class SpecialistEnabledRequest(BaseModel):
    """
    يمثل طلب تفعيل أو تعطيل اختصاصي.
    """
    enabled: bool

