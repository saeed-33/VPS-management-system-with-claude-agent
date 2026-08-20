"""دعم ضوابط صحة خطط المعالجة وأفعالها."""
from __future__ import annotations

from app.core.contracts.remediation.remediation_action import RemediationAction
from app.core.contracts.remediation.remediation_plan_status import RemediationPlanStatus


class _RemediationValidationMixin:
    """يوفر حواجز الأمان والتحقق من روابط الخطة وأفعالها."""

    def _blocked(self, plan_id: str, code: str, message: str) -> dict:
        self._repository.update_plan_status(
            plan_id,
            RemediationPlanStatus.BLOCKED.value,
            denial_reason=message,
        )
        return {
            "applied": False,
            "plan_id": plan_id,
            "blocked_reason": code,
            "message": message,
        }

    @staticmethod
    def _resolve_state_aware_rollback(action: RemediationAction, before_state: str) -> str | None:
        if action.action_type == "start_service" and before_state == "inactive":
            return "stop_service"
        if action.action_type == "stop_service" and before_state == "active":
            return "start_service"
        return None

    @staticmethod
    def _validate_links(*, diagnosis_claim_ids: list[str], evidence_ids: list[str]) -> None:
        if not diagnosis_claim_ids:
            raise ValueError("diagnosis_claim_ids must not be empty.")
        if not evidence_ids:
            raise ValueError("evidence_ids must not be empty.")

    @staticmethod
    def _validate_actions(proposed_actions: list[dict]) -> None:
        if not proposed_actions:
            raise ValueError("proposed_actions must not be empty.")
        forbidden = {"command", "command_text", "shell", "raw_command", "executable"}
        for action in proposed_actions:
            if not isinstance(action, dict):
                raise ValueError("proposed_actions must contain objects.")
            if forbidden.intersection(action):
                raise ValueError("Raw command execution fields are not permitted in remediation plans.")
            if not str(action.get("id", action.get("action_id", "legacy"))).strip():
                raise ValueError("each action requires an id.")
            if not str(action.get("description", action.get("reason", "legacy"))).strip():
                raise ValueError("each action requires a description.")
