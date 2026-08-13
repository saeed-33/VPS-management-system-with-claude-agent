from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ApprovalRequest(BaseModel):
    expires_in_seconds: int = Field(default=3600, ge=60, le=86400)
    scope: dict[str, Any] = Field(default_factory=dict)


class ApprovalDecisionRequest(BaseModel):
    approver: str = Field(min_length=1, max_length=120)
    comment: str | None = Field(default=None, max_length=2000)
    scope: dict[str, Any] | None = None


class ExecuteRemediationRequest(BaseModel):
    approval_id: str = Field(min_length=1, max_length=64)
    server_id: int = Field(ge=1)
    actor: str = Field(min_length=1, max_length=120)
    idempotency_key: str | None = Field(default=None, max_length=255)
    runtime_session_id: str | None = Field(default=None, max_length=128)
    agent_job_id: str | None = Field(default=None, max_length=128)


class RollbackRemediationRequest(BaseModel):
    execution_id: str = Field(min_length=1, max_length=64)
    server_id: int = Field(ge=1)
    actor: str = Field(min_length=1, max_length=120)


class SandboxValidationRequest(BaseModel):
    target_server_id: int = Field(ge=1)
    target_server_name: str = Field(min_length=1, max_length=100)
    target_service: str = Field(min_length=1, max_length=128)
