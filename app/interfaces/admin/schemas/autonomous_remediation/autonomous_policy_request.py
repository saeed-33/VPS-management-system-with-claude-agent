"""
مخططات إدارة سياسات المعالجة الآلية.

تحدد الحقول التي تستخدمها API لإنشاء السياسة أو تعديلها مع إبقاء التحقق من
القيم ضمن قيود Pydantic والعقد الإداري.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AutonomousPolicyRequest(BaseModel):
    """
    يمثل بيانات API اللازمة لإنشاء سياسة معالجة آلية.
    """
    policy_id: str | None = Field(default=None, min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=4000)
    issue_fingerprint: str = Field(min_length=1, max_length=128)
    allowed_action_type: str = Field(default="start_service", min_length=1, max_length=80)
    allowed_target_pattern: str = Field(min_length=1, max_length=128)
    maximum_risk: str = Field(default="low", min_length=1, max_length=20)
    required_evidence: list[str] = Field(default_factory=lambda: [
        "diagnosis", "plan", "sandbox_before", "sandbox_after", "verification"
    ])
    minimum_confidence: float = Field(default=0.0, ge=0, le=1)
    minimum_success_count: int = Field(default=0, ge=0)
    maximum_failure_rate: float = Field(default=0.0, ge=0, le=1)
    maximum_rollback_failure_rate: float = Field(default=0.0, ge=0, le=1)
    allowed_server_ids: list[int] = Field(default_factory=list, min_length=0)
    allowed_server_tags: list[str] = Field(default_factory=list, min_length=0)
    sandbox_required: bool = True
    sandbox_max_age_seconds: int = Field(default=3600, ge=1)
    rollback_required: bool = True
    cooldown_seconds: int = Field(default=0, ge=0)
    max_executions_per_hour: int = Field(default=1, ge=1)
    max_executions_per_day: int = Field(default=3, ge=1)
    max_consecutive_failures: int = Field(default=1, ge=1)
    auto_suspend_on_failure: bool = True
    created_by: str = Field(default="admin", min_length=1, max_length=120)

