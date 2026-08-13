from __future__ import annotations

from uuid import uuid4

from app.infrastructure.database.repositories.remediation_repository import (
    RemediationRepository,
)
from app.core.contracts.remediation import (
    CreateRemediationPlanDTO,
    CreateSandboxResultDTO,
    RemediationPlanStatus,
    RemediationRisk,
    SandboxResultStatus,
)


class RemediationService:
    def __init__(
        self,
        *,
        repository: RemediationRepository,
        automatic_remediation_allowed: bool = False,
    ) -> None:
        self._repository = repository
        self._automatic_remediation_allowed = (
            automatic_remediation_allowed
        )

    def propose_remediation(
        self,
        *,
        investigation_id: str,
        problem_summary: str,
        diagnosis_claim_ids: list[str],
        evidence_ids: list[str],
    ) -> dict:
        self._validate_links(
            diagnosis_claim_ids=diagnosis_claim_ids,
            evidence_ids=evidence_ids,
        )
        if not investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )
        if not problem_summary.strip():
            raise ValueError(
                "problem_summary must not be empty."
            )

        return {
            "investigation_id": investigation_id,
            "problem_summary": problem_summary,
            "diagnosis_claim_ids": list(
                diagnosis_claim_ids
            ),
            "evidence_ids": list(evidence_ids),
            "requires_plan": True,
            "production_application_allowed": False,
        }

    def create_plan(
        self,
        *,
        investigation_id: str,
        title: str,
        problem_summary: str,
        proposed_actions: list[dict],
        diagnosis_claim_ids: list[str],
        evidence_ids: list[str],
        risk_level: str = RemediationRisk.MEDIUM.value,
        rollback_plan: str | None = None,
        plan_id: str | None = None,
    ):
        self._validate_links(
            diagnosis_claim_ids=diagnosis_claim_ids,
            evidence_ids=evidence_ids,
        )
        self._validate_actions(
            proposed_actions
        )

        return self._repository.create_plan(
            CreateRemediationPlanDTO(
                plan_id=plan_id or str(uuid4()),
                investigation_id=investigation_id,
                title=title,
                problem_summary=problem_summary,
                proposed_actions=proposed_actions,
                diagnosis_claim_ids=diagnosis_claim_ids,
                evidence_ids=evidence_ids,
                risk_level=risk_level,
                rollback_plan=rollback_plan,
                metadata={
                    "production_application_allowed": (
                        False
                    )
                },
            )
        )

    def test_in_sandbox(
        self,
        *,
        plan_id: str,
    ):
        plan = self._require_plan(
            plan_id
        )
        actions = plan.proposed_actions or []
        failed_reasons = [
            action.get("sandbox_failure_reason")
            for action in actions
            if isinstance(action, dict)
            and action.get("sandbox_failure_reason")
        ]
        unsupported = [
            action.get("id", "unknown")
            for action in actions
            if isinstance(action, dict)
            and action.get(
                "sandbox_supported",
                True,
            )
            is False
        ]

        passed = (
            not failed_reasons
            and not unsupported
        )
        result_id = str(uuid4())
        logs = [
            "Sandbox validation executed in "
            "isolated dry-run mode.",
        ]
        if unsupported:
            logs.append(
                "Unsupported sandbox actions: "
                + ", ".join(
                    str(item)
                    for item in unsupported
                )
            )
        logs.extend(
            str(item)
            for item in failed_reasons
        )

        return (
            self._repository
            .create_sandbox_result(
                CreateSandboxResultDTO(
                    result_id=result_id,
                    plan_id=plan.plan_id,
                    status=(
                        SandboxResultStatus
                        .PASSED
                        .value
                        if passed
                        else SandboxResultStatus
                        .FAILED
                        .value
                    ),
                    before_evidence_ids=list(
                        plan.evidence_ids or []
                    ),
                    after_evidence_ids=[
                        f"sandbox:{result_id}"
                    ]
                    if passed
                    else [],
                    logs=logs,
                    metadata={
                        "isolated": True,
                        "write_capable": False,
                    },
                )
            )
        )

    def get_plan(
        self,
        plan_id: str,
    ):
        return self._repository.get_plan(
            plan_id
        )

    def get_sandbox_result(
        self,
        result_id: str | None = None,
        *,
        plan_id: str | None = None,
    ):
        if result_id is not None:
            return (
                self._repository
                .get_sandbox_result(result_id)
            )
        if plan_id is not None:
            return (
                self._repository
                .get_latest_sandbox_result_for_plan(
                    plan_id
                )
            )
        raise ValueError(
            "result_id or plan_id is required."
        )

    def request_approval(
        self,
        *,
        plan_id: str,
    ):
        plan = self._require_plan(
            plan_id
        )
        if plan.status != (
            RemediationPlanStatus
            .SANDBOX_PASSED
            .value
        ):
            raise ValueError(
                "Sandbox must pass before approval "
                "can be requested."
            )

        return (
            self._repository
            .update_plan_status(
                plan_id,
                RemediationPlanStatus
                .APPROVAL_REQUESTED
                .value,
                approval_requested=True,
            )
        )

    def apply_approved(
        self,
        *,
        plan_id: str,
        approved_by: str | None = None,
    ) -> dict:
        plan = self._require_plan(
            plan_id
        )

        if plan.status == (
            RemediationPlanStatus
            .SANDBOX_FAILED
            .value
        ):
            return self._blocked(
                plan_id,
                "sandbox_failed",
                "Failed sandbox validation blocks "
                "production application.",
            )

        if plan.status not in {
            RemediationPlanStatus
            .SANDBOX_PASSED
            .value,
            RemediationPlanStatus
            .APPROVAL_REQUESTED
            .value,
            RemediationPlanStatus
            .APPROVED
            .value,
        }:
            return self._blocked(
                plan_id,
                "sandbox_required",
                "Sandbox validation is required "
                "before production application.",
            )

        if plan.risk_level == RemediationRisk.HIGH.value:
            if not approved_by:
                self.request_approval(
                    plan_id=plan_id
                )
                return self._blocked(
                    plan_id,
                    "approval_required",
                    "High-risk remediation requires "
                    "explicit user approval.",
                )
            self._repository.update_plan_status(
                plan_id,
                RemediationPlanStatus
                .APPROVED
                .value,
                approved_by=approved_by,
            )

        if not self._automatic_remediation_allowed:
            return self._blocked(
                plan_id,
                "policy_denied",
                "Project policy denies production "
                "remediation application.",
            )

        self._repository.update_plan_status(
            plan_id,
            RemediationPlanStatus.APPLIED.value,
            approved_by=approved_by,
        )
        return {
            "applied": True,
            "plan_id": plan_id,
        }

    def _blocked(
        self,
        plan_id: str,
        code: str,
        message: str,
    ) -> dict:
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

    def _require_plan(
        self,
        plan_id: str,
    ):
        if not plan_id.strip():
            raise ValueError(
                "plan_id must not be empty."
            )
        plan = self._repository.get_plan(
            plan_id
        )
        if plan is None:
            raise ValueError(
                "Remediation plan not found: "
                f"{plan_id}"
            )
        return plan

    @staticmethod
    def _validate_links(
        *,
        diagnosis_claim_ids: list[str],
        evidence_ids: list[str],
    ) -> None:
        if not diagnosis_claim_ids:
            raise ValueError(
                "diagnosis_claim_ids must not be empty."
            )
        if not evidence_ids:
            raise ValueError(
                "evidence_ids must not be empty."
            )

    @staticmethod
    def _validate_actions(
        proposed_actions: list[dict],
    ) -> None:
        if not proposed_actions:
            raise ValueError(
                "proposed_actions must not be empty."
            )
        for action in proposed_actions:
            if not isinstance(action, dict):
                raise ValueError(
                    "proposed_actions must contain objects."
                )
            if not str(action.get("id", "")).strip():
                raise ValueError(
                    "each action requires an id."
                )
            if not str(action.get("description", "")).strip():
                raise ValueError(
                    "each action requires a description."
                )
