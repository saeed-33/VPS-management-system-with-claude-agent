"""
مخططات الموافقة والتنفيذ والتراجع والتحقق المعزول.

تصف مدخلات دورة معالجة المشكلة في API دون أن تمنح النموذج نفسه صلاحية تنفيذ
التغيير أو تجاوز ضوابط الخدمة.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ApprovalRequest(BaseModel):
    """
    يمثل طلب إنشاء موافقة لخطة معالجة.
    """
    expires_in_seconds: int = Field(default=3600, ge=60, le=86400)
    scope: dict[str, Any] = Field(default_factory=dict)

