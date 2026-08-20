"""Port required by autonomous-remediation capabilities."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from app.core.contracts.autonomous_remediation.autonomous_authorization import (
    AutonomousAuthorization,
)
from app.core.contracts.autonomous_remediation.autonomous_policy_decision import (
    AutonomousPolicyDecision,
)
from app.core.contracts.autonomous_remediation.autonomous_remediation_policy import (
    AutonomousRemediationPolicy,
)


class AutonomousRemediationRepositoryPort(Protocol):
    """Persistence operations required by autonomous-remediation services."""

    def create_policy(self, policy: AutonomousRemediationPolicy) -> Any: ...

    def get_policy(self, policy_id: str) -> Any | None: ...

    def find_duplicate_policy(self, policy: AutonomousRemediationPolicy) -> Any | None: ...

    def list_policies(self, *, status: str | None = None) -> list[Any]: ...

    def update_policy(self, policy_id: str, *, updates: dict, version: int) -> Any: ...

    def resume_policy(self, policy_id: str) -> Any: ...

    def matching_policies(
        self,
        *,
        issue_fingerprint: str,
        action_type: str,
        target: str,
        server_id: int | None,
    ) -> list[Any]: ...

    def candidate_keys(self) -> dict[Any, Any]: ...

    def record_autonomous_success(
        self,
        *,
        policy_id: str,
        policy_version: int | None = None,
        now: datetime | None = None,
    ) -> Any: ...

    def record_autonomous_failure(
        self,
        *,
        policy_id: str,
        policy_version: int | None,
        failure_key: str,
        decision_id: str | None,
        execution_id: str | None = None,
        now: datetime | None = None,
    ) -> Any: ...

    def create_decision(
        self,
        decision: AutonomousPolicyDecision,
        *,
        history: dict,
        metadata: dict | None = None,
    ) -> Any: ...

    def list_decisions(self, *, plan_id: str | None = None, limit: int = 100) -> list[Any]: ...

    def get_decision(self, decision_id: str) -> Any | None: ...

    def create_authorization(self, authorization: AutonomousAuthorization) -> Any: ...

    def consume_authorization(self, authorization_id: str, *, now: datetime) -> Any: ...

    def get_authorization(self, authorization_id: str) -> Any | None: ...

    def list_authorizations(self, *, limit: int = 100) -> list[Any]: ...

    def reserve(
        self,
        *,
        idempotency_key: str,
        owner_token: str,
        policy_id: str,
        plan_id: str,
        plan_fingerprint: str,
        action_type: str,
        target: str,
        server_id: int,
        now: datetime,
        lease_seconds: int = 900,
    ) -> Any: ...

    def get_reservation_by_idempotency_key(self, idempotency_key: str) -> Any | None: ...

    def update_reservation_authorization(
        self,
        reservation_id: str,
        *,
        owner_token: str,
        authorization_id: str,
    ) -> Any: ...

    def finalize_reservation(
        self,
        reservation_id: str,
        *,
        owner_token: str,
        status: str,
        execution_id: str | None = None,
    ) -> Any: ...

    def get_runtime_state(self, policy_id: str) -> Any: ...

    def update_runtime_state(self, policy_id: str, **updates: Any) -> Any: ...

    def append_policy_audit_event(
        self,
        *,
        policy_id: str,
        policy_version: int,
        event_type: str,
        actor: str = "admin",
        payload: dict | None = None,
    ) -> Any: ...

    def list_policy_audit_events(self, policy_id: str) -> list[Any]: ...

    def list_all_policy_audit_events(
        self,
        *,
        policy_id: str | None = None,
        limit: int = 100,
    ) -> list[Any]: ...

    def history(
        self,
        *,
        issue_fingerprint: str,
        action_type: str,
        target: str,
    ) -> Any: ...

    def execution_counts(self, *, policy_id: str, now: datetime) -> dict[str, Any]: ...

