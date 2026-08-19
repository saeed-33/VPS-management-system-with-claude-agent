"""
مخططات الموافقة والتنفيذ والتراجع والتحقق المعزول.

تصف مدخلات دورة معالجة المشكلة في API دون أن تمنح النموذج نفسه صلاحية تنفيذ
التغيير أو تجاوز ضوابط الخدمة.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RollbackRemediationRequest(BaseModel):
    """
    يمثل طلب التراجع عن أثر خطة معالجة.
    """
    execution_id: str = Field(min_length=1, max_length=64)
    server_id: int = Field(ge=1)
    actor: str = Field(min_length=1, max_length=120)

