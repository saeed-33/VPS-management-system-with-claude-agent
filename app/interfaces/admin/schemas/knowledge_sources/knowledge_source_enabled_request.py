"""
مخططات إدارة مصادر المعرفة.

تتحقق من طلبات إنشاء وتعديل وتفعيل المصدر، وتحدد شكل بيانات المصدر التي تعود
إلى الواجهة الإدارية.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class KnowledgeSourceEnabledRequest(BaseModel):
    """
    يمثل طلب تفعيل أو تعطيل مصدر معرفة.
    """
    enabled: bool

