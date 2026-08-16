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


class ApprovalDecisionRequest(BaseModel):
    """
    يمثل قرار قبول أو رفض طلب معالجة مع سبب اختياري.
    """
    approver: str = Field(min_length=1, max_length=120)
    comment: str | None = Field(default=None, max_length=2000)
    scope: dict[str, Any] | None = None


class ExecuteRemediationRequest(BaseModel):
    """
    يمثل خيارات تنفيذ خطة معالجة معتمدة.
    """
    approval_id: str = Field(min_length=1, max_length=64)
    server_id: int = Field(ge=1)
    actor: str = Field(min_length=1, max_length=120)
    idempotency_key: str | None = Field(default=None, max_length=255)
    runtime_session_id: str | None = Field(default=None, max_length=128)
    agent_job_id: str | None = Field(default=None, max_length=128)


class RollbackRemediationRequest(BaseModel):
    """
    يمثل طلب التراجع عن أثر خطة معالجة.
    """
    execution_id: str = Field(min_length=1, max_length=64)
    server_id: int = Field(ge=1)
    actor: str = Field(min_length=1, max_length=120)


class SandboxValidationRequest(BaseModel):
    """
    يمثل خيارات التحقق من خطة معالجة في بيئة معزولة.
    """
    target_server_id: int = Field(ge=1)
    target_server_name: str = Field(min_length=1, max_length=100)
    target_service: str = Field(min_length=1, max_length=128)
