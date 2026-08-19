"""
مخططات الموافقة والتنفيذ والتراجع والتحقق المعزول.

تصف مدخلات دورة معالجة المشكلة في API دون أن تمنح النموذج نفسه صلاحية تنفيذ
التغيير أو تجاوز ضوابط الخدمة.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ApprovalDecisionRequest(BaseModel):
    """
    يمثل قرار قبول أو رفض طلب معالجة مع سبب اختياري.
    """
    approver: str = Field(min_length=1, max_length=120)
    comment: str | None = Field(default=None, max_length=2000)
    scope: dict[str, Any] | None = None

