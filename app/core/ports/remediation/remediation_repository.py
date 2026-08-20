"""Port required by the remediation capability to persist its lifecycle."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from app.core.contracts.remediation.create_remediation_plan_dto import (
    CreateRemediationPlanDTO,
)
from app.core.contracts.remediation.create_sandbox_result_dto import (
    CreateSandboxResultDTO,
)


class RemediationRepositoryPort(Protocol):
    """Persistence operations required by remediation services."""

    def create_plan(self, data: CreateRemediationPlanDTO) -> Any: ...

    def get_plan(self, plan_id: str) -> Any | None: ...

    def create_no_solution_plan(
        self,
        *,
        plan_id: str,
        investigation_id: str,
        title: str,
        problem_summary: str,
        diagnosis_claim_ids: list[str],
        evidence_ids: list[str],
        server_id: int | None = None,
    ) -> Any: ...

    def list_plans(self, *, limit: int = 100, status: str | None = None) -> list[Any]: ...

    def create_sandbox_result(self, data: CreateSandboxResultDTO) -> Any: ...

    def get_sandbox_result(self, result_id: str) -> Any | None: ...

    def get_latest_sandbox_result_for_plan(self, plan_id: str) -> Any | None: ...

    def get_sandbox_validation(self, validation_id: str) -> Any | None: ...

    def get_latest_sandbox_validation(self, plan_id: str) -> Any | None: ...

    def finalize_sandbox_validation(self, **data: Any) -> Any: ...

    def update_sandbox_validation(self, validation_id: str, **updates: Any) -> Any: ...

    def create_approval(
        self,
        *,
        plan_id: str,
        plan_fingerprint: str,
        expires_at: datetime | None = None,
        scope: dict | None = None,
    ) -> Any: ...

    def get_approval(
        self,
        approval_id: str | None = None,
        *,
        plan_id: str | None = None,
    ) -> Any | None: ...

    def decide_approval(
        self,
        approval_id: str,
        *,
        status: str,
        approver: str,
        comment: str | None = None,
        scope: dict | None = None,
    ) -> Any: ...

    def expire_approval(self, approval_id: str) -> Any: ...

    def get_latest_execution_for_plan(self, plan_id: str) -> Any | None: ...

    def create_execution(self, **data: Any) -> Any: ...

    def get_execution(
        self,
        execution_id: str | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> Any | None: ...

    def update_execution(self, execution_id: str, **updates: Any) -> Any: ...

    def mark_interrupted_executions(self) -> int: ...

    def create_evidence(self, **data: Any) -> Any: ...

    def get_evidence(self, evidence_id: str) -> Any | None: ...

    def create_verification(self, **data: Any) -> Any: ...

    def create_rollback(self, **data: Any) -> Any: ...

    def append_audit_event(
        self,
        *,
        plan_id: str,
        event_type: str,
        actor: str | None = None,
        server_id: int | None = None,
        runtime_session_id: str | None = None,
        agent_job_id: str | None = None,
        payload: dict | None = None,
    ) -> Any: ...

    def list_audit_events(self, plan_id: str) -> list[Any]: ...

    def list_all_audit_events(
        self,
        *,
        plan_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[Any]: ...

    def update_plan_status(
        self,
        plan_id: str,
        status: str,
        *,
        approved_by: str | None = None,
        execution_status: str | None = None,
        verification_status: str | None = None,
        rollback_status: str | None = None,
    ) -> Any: ...

