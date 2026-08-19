"""
مخططات إدارة سياسات المعالجة الآلية.

تحدد الحقول التي تستخدمها API لإنشاء السياسة أو تعديلها مع إبقاء التحقق من
القيم ضمن قيود Pydantic والعقد الإداري.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AutonomousPolicyUpdateRequest(BaseModel):
    """
    يمثل الحقول الاختيارية لتعديل سياسة معالجة آلية.
    """
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    allowed_target_pattern: str | None = Field(default=None, min_length=1, max_length=128)
    minimum_confidence: float | None = Field(default=None, ge=0, le=1)
    minimum_success_count: int | None = Field(default=None, ge=0)
    maximum_failure_rate: float | None = Field(default=None, ge=0, le=1)
    maximum_rollback_failure_rate: float | None = Field(default=None, ge=0, le=1)
    updated_by: str = Field(default="admin", min_length=1, max_length=120)

