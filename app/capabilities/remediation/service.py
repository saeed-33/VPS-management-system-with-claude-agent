from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from sqlalchemy.exc import OperationalError

from app.capabilities.remediation.execution import (
    UnavailableVerificationRunner,
    UnavailableWriteRunner,
    VerificationRunner,
    WriteCommandResult,
    WriteCommandRunner,
)
from app.core.contracts.remediation import (
    ApprovalStatus,
    CreateRemediationPlanDTO,
    CreateSandboxResultDTO,
    ExecutionStatus,
    RemediationAction,
    RemediationPlanStatus,
    RemediationRisk,
    RollbackStatus,
    VerificationStatus,
)
from app.core.policies.remediation_policy import RemediationPolicyEngine
from app.core.policies.remediation_risk import RemediationRiskClassifier
from app.core.policies.remediation_tools import (
    NamedWriteToolRegistry,
    build_default_write_tool_registry,
)
from app.core.utils.datetime import utc_now
from app.infrastructure.database.repositories.remediation_repository import RemediationRepository


class RemediationService:
    def __init__(
        self,
        *,
        repository: RemediationRepository,
        automatic_remediation_allowed: bool = False,
        write_tool_registry: NamedWriteToolRegistry | None = None,
        write_runner: WriteCommandRunner | None = None,
        verification_runner: VerificationRunner | None = None,
    ) -> None:
        self._repository = repository
        self._automatic_remediation_allowed = automatic_remediation_allowed
        self._write_tools = write_tool_registry or build_default_write_tool_registry()
        self._risk_classifier = RemediationRiskClassifier(self._write_tools)
        self._policy = RemediationPolicyEngine(automatic_remediation_allowed=automatic_remediation_allowed)
        self._write_runner = write_runner or UnavailableWriteRunner()
        self._verification_runner = verification_runner or UnavailableVerificationRunner()

    def propose_remediation(self, *, investigation_id: str, problem_summary: str,
                            diagnosis_claim_ids: list[str], evidence_ids: list[str]) -> dict:
        self._validate_links(diagnosis_claim_ids=diagnosis_claim_ids, evidence_ids=evidence_ids)
        if not investigation_id.strip():
            raise ValueError("investigation_id must not be empty.")
        if not problem_summary.strip():
            raise ValueError("problem_summary must not be empty.")
        return {
            "investigation_id": investigation_id,
            "problem_summary": problem_summary,
            "diagnosis_claim_ids": list(diagnosis_claim_ids),
            "evidence_ids": list(evidence_ids),
            "requires_plan": True,
            "production_application_allowed": False,
            "automatic_remediation_allowed": self._automatic_remediation_allowed,
        }

    def create_plan(self, *, investigation_id: str, title: str, problem_summary: str,
                    proposed_actions: list[dict], diagnosis_claim_ids: list[str], evidence_ids: list[str],
                    risk_level: str = RemediationRisk.MEDIUM.value, rollback_plan: str | None = None,
                    plan_id: str | None = None, server_id: int | None = None):
        self._validate_links(diagnosis_claim_ids=diagnosis_claim_ids, evidence_ids=evidence_ids)
        self._validate_actions(proposed_actions)
        action_models = [RemediationAction.from_dict(action) for action in proposed_actions]
        registered = [self._write_tools.get(action.action_type) is not None for action in action_models]
        deterministic_risk = self._risk_classifier.classify_actions(action_models)
        requested_risk = RemediationRisk(risk_level)
        effective_risk = deterministic_risk if all(registered) else requested_risk
        # User-supplied risk may only increase the deterministic result.
        risk_order = {risk: index for index, risk in enumerate(RemediationRisk)}
        if risk_order[requested_risk] > risk_order[effective_risk]:
            effective_risk = requested_risk
        return self._repository.create_plan(
            CreateRemediationPlanDTO(
                plan_id=plan_id or str(uuid4()),
                investigation_id=investigation_id,
                title=title,
                problem_summary=problem_summary,
                proposed_actions=list(proposed_actions),
                diagnosis_claim_ids=diagnosis_claim_ids,
                evidence_ids=evidence_ids,
                risk_level=effective_risk.value,
                rollback_plan=rollback_plan,
                metadata={
                    "production_application_allowed": False,
                    "automatic_remediation_allowed": self._automatic_remediation_allowed,
                    "registered_actions": registered,
                },
                server_id=server_id,
            )
        )

    def record_no_solution_found(self, *, investigation_id: str, title: str,
                                 problem_summary: str, diagnosis_claim_ids: list[str],
                                 evidence_ids: list[str], server_id: int | None = None,
                                 plan_id: str | None = None):
        self._validate_links(diagnosis_claim_ids=diagnosis_claim_ids, evidence_ids=evidence_ids)
        return self._repository.create_no_solution_plan(
            plan_id=plan_id or str(uuid4()), investigation_id=investigation_id,
            title=title, problem_summary=problem_summary,
            diagnosis_claim_ids=diagnosis_claim_ids, evidence_ids=evidence_ids,
            server_id=server_id,
        )

    def test_in_sandbox(self, *, plan_id: str):
        plan = self._require_plan(plan_id)
        actions = plan.proposed_actions or []
        failed_reasons = [action.get("sandbox_failure_reason") for action in actions if isinstance(action, dict) and action.get("sandbox_failure_reason")]
        unsupported = [action.get("id", "unknown") for action in actions if isinstance(action, dict) and action.get("sandbox_supported", True) is False]
        for action_data in actions:
            action = RemediationAction.from_dict(action_data)
            if action.action_type != "legacy":
                try:
                    self._write_tools.resolve(action)
                except ValueError as exc:
                    failed_reasons.append(str(exc))
        passed = not failed_reasons and not unsupported
        result_id = str(uuid4())
        logs = ["Sandbox validation executed in isolated dry-run mode."]
        if unsupported:
            logs.append("Unsupported sandbox actions: " + ", ".join(str(item) for item in unsupported))
        logs.extend(str(item) for item in failed_reasons)
        result = self._repository.create_sandbox_result(
            CreateSandboxResultDTO(
                result_id=result_id,
                plan_id=plan.plan_id,
                status="passed" if passed else "failed",
                before_evidence_ids=list(plan.evidence_ids or []),
                after_evidence_ids=[f"sandbox:{result_id}"] if passed else [],
                logs=logs,
                metadata={"isolated": True, "write_capable": False},
            )
        )
        self._audit(plan, "sandbox_passed" if passed else "sandbox_failed", {"result_id": result_id})
        return result

    def get_plan(self, plan_id: str):
        return self._repository.get_plan(plan_id)

    def get_approval(self, approval_id: str | None = None, *, plan_id: str | None = None):
        return self._repository.get_approval(approval_id, plan_id=plan_id)

    def get_latest_execution(self, plan_id: str):
        return self._repository.get_latest_execution_for_plan(plan_id)

    def list_plans(self, *, limit: int = 100, status: str | None = None):
        return self._repository.list_plans(limit=limit, status=status)

    def get_sandbox_result(self, result_id: str | None = None, *, plan_id: str | None = None):
        if result_id is not None:
            return self._repository.get_sandbox_result(result_id)
        if plan_id is not None:
            return self._repository.get_latest_sandbox_result_for_plan(plan_id)
        raise ValueError("result_id or plan_id is required.")

    def request_approval(self, *, plan_id: str, expires_in_seconds: int = 3600, scope: dict | None = None):
        plan = self._require_plan(plan_id)
        if plan.status != RemediationPlanStatus.SANDBOX_PASSED.value:
            raise ValueError("Sandbox must pass before approval can be requested.")
        approval = self._repository.create_approval(
            plan_id=plan_id,
            plan_fingerprint=plan.plan_fingerprint,
            expires_at=utc_now() + timedelta(seconds=expires_in_seconds),
            scope=scope,
        )
        self._audit(plan, "approval_requested", {"approval_id": approval.approval_id})
        return approval

    def approve(self, *, approval_id: str, approver: str, comment: str | None = None, scope: dict | None = None):
        if not approver.strip():
            raise ValueError("approver must not be empty.")
        approval = self._repository.get_approval(approval_id)
        if approval is None:
            raise ValueError("Approval not found.")
        if approval.expires_at is not None:
            expires_at = approval.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=utc_now().tzinfo)
            if expires_at <= utc_now():
                self._repository.expire_approval(approval_id)
                raise ValueError("Approval has expired.")
        plan = self._require_plan(approval.plan_id)
        if approval.plan_fingerprint != plan.plan_fingerprint:
            raise ValueError("Approval fingerprint is stale.")
        result = self._repository.decide_approval(approval_id, status=ApprovalStatus.APPROVED.value, approver=approver, comment=comment, scope=scope)
        self._audit(plan, "approval_granted", {"approval_id": approval_id, "approver": approver})
        return result

    def reject(self, *, approval_id: str, approver: str, comment: str | None = None):
        if not approver.strip():
            raise ValueError("approver must not be empty.")
        approval = self._repository.get_approval(approval_id)
        if approval is None:
            raise ValueError("Approval not found.")
        result = self._repository.decide_approval(approval_id, status=ApprovalStatus.REJECTED.value, approver=approver, comment=comment)
        plan = self._require_plan(approval.plan_id)
        self._audit(plan, "approval_rejected", {"approval_id": approval_id, "approver": approver})
        return result

    def expire_approval(self, *, approval_id: str):
        approval = self._repository.expire_approval(approval_id)
        plan = self._require_plan(approval.plan_id)
        self._audit(plan, "approval_expired", {"approval_id": approval_id})
        return approval

    def apply_approved(self, *, plan_id: str, approval_id: str | None = None, approved_by: str | None = None,
                       server_id: int | None = None, actor: str | None = None,
                       idempotency_key: str | None = None, runtime_session_id: str | None = None,
                       agent_job_id: str | None = None) -> dict:
        plan = self._require_plan(plan_id)
        if plan.status == RemediationPlanStatus.SANDBOX_FAILED.value:
            return self._blocked(plan_id, "sandbox_failed", "Failed sandbox validation blocks production application.")
        if approval_id is None:
            # Legacy callers cannot self-approve. Preserve the historical
            # response shape while requiring the new persisted approval path.
            if plan.risk_level in {RemediationRisk.HIGH.value, RemediationRisk.CRITICAL.value}:
                return self._blocked(plan_id, "approval_required", "Explicit persisted user approval is required.")
            return self._blocked(plan_id, "policy_denied", "Production remediation requires persisted human approval.")
        approval = self._repository.get_approval(approval_id)
        actions = [RemediationAction.from_dict(action) for action in (plan.proposed_actions or [])]
        if server_id is None or plan.server_id is None or server_id != plan.server_id:
            return self._blocked(plan_id, "wrong_or_missing_server", "Execution must target the original approved server.")
        if len(actions) == 1:
            early_key = idempotency_key or f"{plan.plan_id}:{plan.plan_version}:{actions[0].action_id or actions[0].action_type}"
            existing = self._repository.get_execution(idempotency_key=early_key)
            if existing is not None:
                return {"applied": existing.status == ExecutionStatus.SUCCEEDED.value, "idempotent": True, "execution": existing}
        decision = self._policy.evaluate_execution(
            plan=plan, approval=approval, requested_server_id=server_id, now=utc_now()
        )
        if not decision.allowed:
            return self._blocked(plan_id, decision.reasons[0] if decision.reasons else "policy_denied", "; ".join(decision.reasons))
        if len(actions) != 1:
            return self._blocked(plan_id, "multiple_actions_require_review", "Only one named action may execute per supervised plan.")
        action = actions[0]
        try:
            tool = self._write_tools.resolve(action)
        except ValueError:
            return self._blocked(plan_id, "unknown_write_tool", "Action is not in the registered remediation write-tool registry.")
        if not tool.rollback_action:
            return self._blocked(plan_id, "rollback_not_supported", "A supervised write requires a registered rollback action.")
        key = idempotency_key or f"{plan.plan_id}:{plan.plan_version}:{action.action_id or action.action_type}"
        execution_id = str(uuid4())
        before_ids = [f"before:{execution_id}"]
        execution = self._repository.create_execution(
            execution_id=execution_id, plan_id=plan.plan_id,
            action_id=action.action_id or action.action_type, server_id=server_id,
            status=ExecutionStatus.RUNNING.value, idempotency_key=key,
            actor=actor or approved_by, runtime_session_id=runtime_session_id,
            agent_job_id=agent_job_id, before_evidence_ids=before_ids,
            after_evidence_ids=[], started_at=utc_now(), exit_status=None,
            stdout="", stderr="", error=None, execution_metadata={"command_registry": tool.name},
        )
        self._repository.update_plan_status(plan_id, RemediationPlanStatus.EXECUTING.value, execution_status=ExecutionStatus.RUNNING.value)
        self._audit(plan, "execution_started", {"execution_id": execution.execution_id, "idempotency_key": key}, actor=actor,
                    runtime_session_id=runtime_session_id, agent_job_id=agent_job_id)
        result = self._write_runner.run(server_id=server_id, action=action, command=tool.command_for(action), timeout_seconds=tool.timeout_seconds)
        if not isinstance(result, WriteCommandResult):
            result = WriteCommandResult(**result)
        after_ids = [f"after:{execution_id}"]
        if not result.success:
            self._repository.update_execution(execution.execution_id, status=ExecutionStatus.FAILED.value, after_evidence_ids=after_ids,
                                               exit_status=result.exit_status, stdout=result.stdout, stderr=result.stderr,
                                               error=result.error or "write_execution_failed", completed_at=utc_now())
            self._repository.update_plan_status(plan_id, RemediationPlanStatus.ROLLBACK_REQUIRED.value,
                                                execution_status=ExecutionStatus.FAILED.value, rollback_status=RollbackStatus.REQUIRED.value)
            self._audit(plan, "execution_failed", {"execution_id": execution.execution_id, "error": result.error}, actor=actor,
                        runtime_session_id=runtime_session_id, agent_job_id=agent_job_id)
            return {"applied": False, "plan_id": plan_id, "execution_id": execution.execution_id, "blocked_reason": "execution_failed", "message": result.error or "Write execution failed."}
        self._repository.update_execution(execution.execution_id, status=ExecutionStatus.SUCCEEDED.value, after_evidence_ids=after_ids,
                                          exit_status=result.exit_status or 0, stdout=result.stdout, stderr=result.stderr, completed_at=utc_now())
        verified, details = self._verification_runner.verify(server_id=server_id, action=action)
        verification = self._repository.create_verification(
            verification_id=str(uuid4()), execution_id=execution.execution_id,
            status=VerificationStatus.VERIFIED.value if verified else VerificationStatus.FAILED.value,
            before_evidence_ids=before_ids, after_evidence_ids=after_ids, details=details,
        )
        if not verified:
            self._repository.update_plan_status(plan_id, RemediationPlanStatus.ROLLBACK_REQUIRED.value,
                                                execution_status=ExecutionStatus.SUCCEEDED.value,
                                                verification_status=VerificationStatus.FAILED.value,
                                                rollback_status=RollbackStatus.REQUIRED.value)
            self._audit(plan, "verification_failed", {"execution_id": execution.execution_id, "verification_id": verification.verification_id}, actor=actor,
                        runtime_session_id=runtime_session_id, agent_job_id=agent_job_id)
            return {"applied": False, "plan_id": plan_id, "execution_id": execution.execution_id, "blocked_reason": "verification_failed", "message": "Write completed but verification failed."}
        self._repository.update_plan_status(plan_id, RemediationPlanStatus.SUCCEEDED.value,
                                            execution_status=ExecutionStatus.SUCCEEDED.value,
                                            verification_status=VerificationStatus.VERIFIED.value,
                                            rollback_status=RollbackStatus.NOT_REQUIRED.value)
        self._audit(plan, "execution_succeeded", {"execution_id": execution.execution_id, "verification_id": verification.verification_id}, actor=actor,
                    runtime_session_id=runtime_session_id, agent_job_id=agent_job_id)
        return {"applied": True, "plan_id": plan_id, "execution_id": execution.execution_id, "verified": True, "idempotent": False}

    def rollback(self, *, plan_id: str, execution_id: str, actor: str | None = None, server_id: int | None = None) -> dict:
        plan = self._require_plan(plan_id)
        execution = self._repository.get_execution(execution_id)
        if execution is None or execution.plan_id != plan_id:
            return self._blocked(plan_id, "execution_not_found", "Execution does not belong to this plan.")
        actions = [RemediationAction.from_dict(action) for action in (plan.proposed_actions or [])]
        if len(actions) != 1:
            return self._blocked(plan_id, "rollback_not_supported", "Rollback requires one registered action.")
        action = actions[0]
        tool = self._write_tools.get(action.action_type)
        if tool is None or not tool.rollback_action or server_id is None or plan.server_id != server_id:
            return self._blocked(plan_id, "rollback_policy_denied", "Rollback requires the registered reverse action and original server.")
        reverse = RemediationAction(action_type=tool.rollback_action, target=action.target, action_id=f"rollback:{action.action_id or action.action_type}")
        reverse_tool = self._write_tools.resolve(reverse)
        result = self._write_runner.run(server_id=server_id, action=reverse, command=reverse_tool.command_for(reverse), timeout_seconds=reverse_tool.timeout_seconds)
        success = result.success if isinstance(result, WriteCommandResult) else bool(result.get("success"))
        rollback_status = RollbackStatus.SUCCEEDED.value if success else RollbackStatus.FAILED.value
        rollback = self._repository.create_rollback(
            rollback_id=str(uuid4()), execution_id=execution_id, status=rollback_status,
            before_evidence_ids=[f"rollback-before:{execution_id}"], after_evidence_ids=[f"rollback-after:{execution_id}"],
            details={"action_type": reverse.action_type, "error": getattr(result, "error", None)},
        )
        self._repository.update_plan_status(plan_id, RemediationPlanStatus.ROLLBACK_SUCCEEDED.value if success else RemediationPlanStatus.ROLLBACK_FAILED.value,
                                            rollback_status=rollback_status)
        self._audit(plan, "rollback_succeeded" if success else "rollback_failed", {"rollback_id": rollback.rollback_id}, actor=actor)
        return {"rolled_back": success, "plan_id": plan_id, "rollback_id": rollback.rollback_id}

    def list_audit_events(self, plan_id: str):
        return self._repository.list_audit_events(plan_id)

    def recover_interrupted_executions(self) -> int:
        return self._repository.mark_interrupted_executions()

    def _blocked(self, plan_id: str, code: str, message: str) -> dict:
        self._repository.update_plan_status(plan_id, RemediationPlanStatus.BLOCKED.value, denial_reason=message)
        return {"applied": False, "plan_id": plan_id, "blocked_reason": code, "message": message}

    def _require_plan(self, plan_id: str):
        if not plan_id.strip():
            raise ValueError("plan_id must not be empty.")
        plan = self._repository.get_plan(plan_id)
        if plan is None:
            raise ValueError(f"Remediation plan not found: {plan_id}")
        return plan

    def _audit(self, plan, event_type: str, payload: dict, actor: str | None = None,
               runtime_session_id: str | None = None, agent_job_id: str | None = None) -> None:
        try:
            self._repository.append_audit_event(plan_id=plan.plan_id, event_type=event_type, actor=actor,
                                                server_id=getattr(plan, "server_id", None),
                                                runtime_session_id=runtime_session_id,
                                                agent_job_id=agent_job_id, payload=payload)
        except OperationalError:
            # C.14 legacy test databases contain only the two original
            # remediation tables. The Phase 5 migration creates the audit
            # table; do not make legacy read/sandbox behavior unusable while
            # that additive migration is being applied.
            return

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
