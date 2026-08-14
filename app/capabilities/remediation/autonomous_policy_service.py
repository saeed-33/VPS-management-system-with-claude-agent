from __future__ import annotations

import re
from uuid import uuid4

from app.core.contracts.autonomous_remediation import (
    AutonomousPolicyStatus,
    AutonomousRemediationPolicy,
    V1_AUTONOMOUS_ACTIONS,
)


class AutonomousPolicyService:
    """Human/admin policy registry. Claude never receives this service."""

    def __init__(self, *, repository) -> None:
        self._repository = repository

    def create(self, **values):
        policy = self._validate(values, policy_id=values.get("policy_id") or str(uuid4()), version=1)
        return self._repository.create_policy(policy)

    def get(self, policy_id: str):
        return self._repository.get_policy(policy_id)

    def list(self, *, status: str | None = None):
        return self._repository.list_policies(status=status)

    def update(self, policy_id: str, **updates):
        current = self._repository.get_policy(policy_id)
        if current is None:
            raise ValueError("Autonomous policy not found.")
        values = self._model_values(current)
        values.update(updates)
        policy = self._validate(values, policy_id=policy_id, version=current.version + 1)
        return self._repository.update_policy(policy_id, updates=self._model_values(policy), version=policy.version)

    def enable(self, policy_id: str, *, actor: str = "admin"):
        current = self._require(policy_id)
        result = self._repository.resume_policy(policy_id)
        self._audit_policy(result, "autonomous_policy_enabled", {"previous_status": current.status}, actor=actor)
        return result

    def disable(self, policy_id: str, *, actor: str = "admin"):
        current = self._require(policy_id)
        result = self._repository.update_policy(
            policy_id, updates={"status": AutonomousPolicyStatus.DISABLED.value}, version=current.version
        )
        self._audit_policy(result, "autonomous_policy_disabled", {"previous_status": current.status}, actor=actor)
        return result

    def suspend(self, policy_id: str, *, reason: str, actor: str = "admin"):
        current = self._require(policy_id)
        result = self._repository.update_policy(policy_id, updates={"status": AutonomousPolicyStatus.SUSPENDED.value}, version=current.version)
        self._audit_policy(result, "autonomous_policy_suspended", {"reason": reason, "operator": True}, actor=actor)
        return result

    def resume(self, policy_id: str, *, actor: str = "admin"):
        current = self._require(policy_id)
        result = self._repository.resume_policy(policy_id)
        self._audit_policy(result, "autonomous_policy_resumed", {"new_runtime_epoch": True}, actor=actor)
        return result

    def _audit_policy(self, policy, event_type: str, payload: dict, *, actor: str = "admin") -> None:
        append = getattr(self._repository, "append_policy_audit_event", None)
        if append is not None:
            append(
                policy_id=policy.policy_id,
                policy_version=policy.version,
                event_type=event_type,
                actor=actor,
                payload=payload,
            )

    def _require(self, policy_id: str):
        current = self._repository.get_policy(policy_id)
        if current is None:
            raise ValueError("Autonomous policy not found.")
        return current

    @staticmethod
    def _model_to_contract(model):
        if model is None:
            return None
        return AutonomousRemediationPolicy(
            policy_id=model.policy_id, name=model.name, description=model.description,
            status=AutonomousPolicyStatus(model.status), version=model.version,
            issue_fingerprint=model.issue_fingerprint, allowed_action_type=model.allowed_action_type,
            allowed_target_pattern=model.allowed_target_pattern, maximum_risk=model.maximum_risk,
            minimum_confidence=model.minimum_confidence, required_evidence=tuple(model.required_evidence or ()),
            minimum_success_count=model.minimum_success_count, maximum_failure_rate=model.maximum_failure_rate,
            maximum_rollback_failure_rate=model.maximum_rollback_failure_rate,
            allowed_server_ids=tuple(model.allowed_server_ids or ()), allowed_server_tags=tuple(model.allowed_server_tags or ()),
            sandbox_required=model.sandbox_required, sandbox_max_age_seconds=model.sandbox_max_age_seconds,
            rollback_required=model.rollback_required, cooldown_seconds=model.cooldown_seconds,
            max_executions_per_hour=model.max_executions_per_hour, max_executions_per_day=model.max_executions_per_day,
            max_consecutive_failures=model.max_consecutive_failures, auto_suspend_on_failure=model.auto_suspend_on_failure,
            created_by=model.created_by, updated_by=model.updated_by, created_at=model.created_at, updated_at=model.updated_at,
        )

    @staticmethod
    def _validate(values: dict, *, policy_id: str, version: int) -> AutonomousRemediationPolicy:
        action = str(values.get("allowed_action_type") or "")
        if action not in V1_AUTONOMOUS_ACTIONS:
            raise ValueError("Phase 7 V1 policies may allow only start_service.")
        target = str(values.get("allowed_target_pattern") or "")
        if not target or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.@*-]{0,127}", target):
            raise ValueError("allowed_target_pattern is invalid.")
        if any(token in target for token in ("/", "\\", ";", "|", "&", "`", "$", "*", "?")):
            raise ValueError("Phase 7 V1 requires an explicit service target; wildcard patterns are not permitted.")
        if not values.get("issue_fingerprint"):
            raise ValueError("issue_fingerprint must not be empty.")
        maximum_risk = str(values.get("maximum_risk") or "low")
        if maximum_risk != "low":
            raise ValueError("Phase 7 V1 maximum_risk must be low.")
        return AutonomousRemediationPolicy(
            policy_id=policy_id, name=str(values.get("name") or ""), description=str(values.get("description") or ""),
            status=AutonomousPolicyStatus(str(values.get("status") or AutonomousPolicyStatus.DISABLED.value)),
            version=version, issue_fingerprint=str(values.get("issue_fingerprint") or ""),
            allowed_action_type=action, allowed_target_pattern=target,
            maximum_risk=maximum_risk, minimum_confidence=float(values.get("minimum_confidence", 0.0)),
            required_evidence=tuple(values.get("required_evidence") or ("diagnosis", "plan", "sandbox_before", "sandbox_after", "verification")),
            minimum_success_count=int(values.get("minimum_success_count", 0)),
            maximum_failure_rate=float(values.get("maximum_failure_rate", 0.0)),
            maximum_rollback_failure_rate=float(values.get("maximum_rollback_failure_rate", 0.0)),
            allowed_server_ids=tuple(int(item) for item in (values.get("allowed_server_ids") or ())),
            allowed_server_tags=tuple(str(item) for item in (values.get("allowed_server_tags") or ())),
            sandbox_required=bool(values.get("sandbox_required", True)), sandbox_max_age_seconds=int(values.get("sandbox_max_age_seconds", 3600)),
            rollback_required=bool(values.get("rollback_required", True)), cooldown_seconds=int(values.get("cooldown_seconds", 0)),
            max_executions_per_hour=int(values.get("max_executions_per_hour", 1)), max_executions_per_day=int(values.get("max_executions_per_day", 3)),
            max_consecutive_failures=int(values.get("max_consecutive_failures", 1)), auto_suspend_on_failure=bool(values.get("auto_suspend_on_failure", True)),
            created_by=str(values.get("created_by") or "admin"), updated_by=str(values.get("updated_by") or values.get("created_by") or "admin"),
        )

    @staticmethod
    def _model_values(model) -> dict:
        return {key: getattr(model, key) for key in (
            "name", "description", "status", "issue_fingerprint", "allowed_action_type", "allowed_target_pattern", "maximum_risk",
            "minimum_confidence", "required_evidence", "minimum_success_count", "maximum_failure_rate", "maximum_rollback_failure_rate",
            "allowed_server_ids", "allowed_server_tags", "sandbox_required", "sandbox_max_age_seconds", "rollback_required", "cooldown_seconds",
            "max_executions_per_hour", "max_executions_per_day", "max_consecutive_failures", "auto_suspend_on_failure", "created_by", "updated_by",
        ) if hasattr(model, key)}
