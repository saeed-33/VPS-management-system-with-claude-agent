"""
مخططات الموافقة والتنفيذ والتراجع والتحقق المعزول.

تصف مدخلات دورة معالجة المشكلة في API دون أن تمنح النموذج نفسه صلاحية تنفيذ
التغيير أو تجاوز ضوابط الخدمة.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SandboxValidationRequest(BaseModel):
    """
    يمثل خيارات التحقق من خطة معالجة في بيئة معزولة.
    """
    target_server_id: int = Field(ge=1)
    target_server_name: str = Field(min_length=1, max_length=100)
    target_service: str = Field(min_length=1, max_length=128)

