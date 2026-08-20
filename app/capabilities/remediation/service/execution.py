"""
إدارة دورة معالجة المشكلة بعد التشخيص.

تنشئ الخدمة خطة قابلة للفحص، تتحقق منها في بيئة معزولة، تطلب الموافقة قبل
التغيير، تنفذ الخطة المعتمدة، وتتحقق من النتيجة أو تنفذ التراجع مع سجل تدقيق.
"""
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from sqlalchemy.exc import OperationalError

from app.core.ports.remediation.service_state_evidence_collector import ServiceStateEvidenceCollector
from app.core.contracts.remediation.service_state_observation import ServiceStateObservation
from app.capabilities.remediation.execution.fallback_evidence_collector import FallbackEvidenceCollector
from app.capabilities.remediation.execution.fallback_verification_runner import FallbackVerificationRunner
from app.capabilities.remediation.execution.fallback_write_runner import FallbackWriteRunner
from app.core.ports.remediation.verification_runner import VerificationRunner
from app.core.contracts.remediation.write_command_result import WriteCommandResult
from app.core.ports.remediation.write_command_runner import WriteCommandRunner
from app.capabilities.remediation.sandbox_runtime import NativeSandboxRuntime
from app.core.contracts.sandbox_validation.sandbox_runtime_check import SandboxRuntimeCheck
from app.core.contracts.sandbox_validation.sandbox_target import SandboxTarget
from app.core.contracts.sandbox_validation.sandbox_validation_status import SandboxValidationStatus
from app.core.policies.sandbox_validation import validate_sandbox_target
from app.core.contracts.remediation.approval_status import ApprovalStatus
from app.core.contracts.remediation.create_remediation_plan_dto import CreateRemediationPlanDTO
from app.core.contracts.remediation.create_sandbox_result_dto import CreateSandboxResultDTO
from app.core.contracts.remediation.execution_status import ExecutionStatus
from app.core.contracts.remediation.remediation_action import RemediationAction
from app.core.contracts.remediation.remediation_plan_status import RemediationPlanStatus
from app.core.contracts.remediation.remediation_risk import RemediationRisk
from app.core.contracts.remediation.rollback_status import RollbackStatus
from app.core.contracts.remediation.verification_status import VerificationStatus
from app.core.contracts.autonomous_remediation.autonomous_authorization_status import AutonomousAuthorizationStatus
from app.core.contracts.autonomous_remediation.autonomous_authorization import AutonomousAuthorization
from app.core.contracts.analysis.error_classification import ErrorClassification
from app.core.policies.remediation_policy import RemediationPolicyEngine
from app.core.policies.remediation_risk import RemediationRiskClassifier
from app.core.policies.remediation_tools.named_write_tool_registry import NamedWriteToolRegistry
from app.core.policies.remediation_tools.factories import build_default_write_tool_registry
from app.core.utils.datetime import utc_now


class _RemediationExecutionMixin:
    """ينظم مجموعة من عمليات خدمة المعالجة."""

    def apply_approved(self, *, plan_id: str, approval_id: str | None = None, approved_by: str | None = None,
                       server_id: int | None = None, actor: str | None = None,
                       idempotency_key: str | None = None, runtime_session_id: str | None = None,
                       agent_job_id: str | None = None,
                       autonomous_authorization: AutonomousAuthorization | None = None) -> dict:
        """
        ينفذ الخطة بعد التحقق من الموافقة والروابط والأدلة، ثم يسجل النتيجة.
        """
        plan = self._require_plan(plan_id)
        if plan.status == RemediationPlanStatus.SANDBOX_FAILED.value:
            return self._blocked(plan_id, "sandbox_failed", "Failed sandbox validation blocks production application.")
        if autonomous_authorization is not None:
            if approval_id is not None:
                return self._blocked(plan_id, "authorization_scope_conflict", "Autonomous authorization cannot be combined with human approval input.")
            if autonomous_authorization.plan_id != plan.plan_id or autonomous_authorization.plan_fingerprint != plan.plan_fingerprint:
                return self._blocked(plan_id, "authorization_stale", "Autonomous authorization is not bound to the current plan.")
            if autonomous_authorization.server_id != server_id:
                return self._blocked(plan_id, "authorization_stale", "Autonomous authorization is not bound to the requested server.")
            if autonomous_authorization.status != AutonomousAuthorizationStatus.CONSUMED:
                return self._blocked(plan_id, "authorization_stale", "Autonomous authorization is not consumed.")
            if plan.status not in {RemediationPlanStatus.SANDBOX_PASSED.value, RemediationPlanStatus.APPROVED.value}:
                return self._blocked(plan_id, "plan_not_ready", "Autonomous execution requires a passed sandbox plan.")
        elif approval_id is None:
            # لا تكفي الطلبات القديمة لاعتماد التغيير؛ نحافظ على شكل الرد
            # ونطلب في الوقت نفسه موافقة محفوظة يمكن مراجعتها.
            if plan.risk_level in {RemediationRisk.HIGH.value, RemediationRisk.CRITICAL.value}:
                return self._blocked(plan_id, "approval_required", "Explicit persisted user approval is required.")
            return self._blocked(plan_id, "policy_denied", "Production remediation requires persisted human approval.")
        approval = self._repository.get_approval(approval_id) if autonomous_authorization is None else None
        actions = [RemediationAction.from_dict(action) for action in (plan.proposed_actions or [])]
        if server_id is None or plan.server_id is None or server_id != plan.server_id:
            return self._blocked(plan_id, "wrong_or_missing_server", "Execution must target the original approved server.")
        if len(actions) == 1:
            early_key = idempotency_key or f"{plan.plan_id}:{plan.plan_version}:{actions[0].action_id or actions[0].action_type}"
            existing = self._repository.get_execution(idempotency_key=early_key)
            if existing is not None:
                return {"applied": existing.status == ExecutionStatus.SUCCEEDED.value, "idempotent": True, "execution": existing}
        if autonomous_authorization is None:
            decision = self._policy.evaluate_execution(
                plan=plan, approval=approval, requested_server_id=server_id, now=utc_now()
            )
            if not decision.allowed:
                return self._blocked(plan_id, decision.reasons[0] if decision.reasons else "policy_denied", "; ".join(decision.reasons))
        if len(actions) != 1:
            return self._blocked(plan_id, "multiple_actions_require_review", "Only one named action may execute per supervised plan.")
        action = actions[0]
        if autonomous_authorization is not None and (
            autonomous_authorization.action_type != action.action_type
            or autonomous_authorization.target != action.target
        ):
            return self._blocked(plan_id, "authorization_stale", "Autonomous authorization is not bound to the current named action.")
        try:
            tool = self._write_tools.resolve(action)
        except ValueError:
            return self._blocked(plan_id, "unknown_write_tool", "Action is not in the registered remediation write-tool registry.")
        if not tool.rollback_action:
            return self._blocked(plan_id, "rollback_not_supported", "A supervised write requires a registered rollback action.")
        key = idempotency_key or f"{plan.plan_id}:{plan.plan_version}:{action.action_id or action.action_type}"
        execution_id = str(uuid4())
        before_evidence = self._collect_evidence(
            plan=plan, execution_id=execution_id, server_id=server_id,
            service=action.target, phase="before",
        )
        if before_evidence is None:
            return self._blocked(plan_id, "before_evidence_unavailable", "Project-owned before Evidence is required before a write.")
        before_ids = [before_evidence.evidence_id]
        execution = self._repository.create_execution(
            execution_id=execution_id, plan_id=plan.plan_id,
            action_id=action.action_id or action.action_type, server_id=server_id,
            status=ExecutionStatus.RUNNING.value, idempotency_key=key,
            actor=actor or approved_by, runtime_session_id=runtime_session_id,
            agent_job_id=agent_job_id, before_evidence_ids=before_ids,
            after_evidence_ids=[], started_at=utc_now(), exit_status=None,
            stdout="", stderr="", error=None, execution_metadata={
                "command_registry": tool.name,
                "autonomous": autonomous_authorization is not None,
                "authorization_id": autonomous_authorization.authorization_id if autonomous_authorization else None,
                "policy_id": autonomous_authorization.policy_id if autonomous_authorization else None,
                "policy_version": autonomous_authorization.policy_version if autonomous_authorization else None,
            },
        )
        self._repository.update_plan_status(plan_id, RemediationPlanStatus.EXECUTING.value, execution_status=ExecutionStatus.RUNNING.value)
        self._audit(plan, "execution_started", {"execution_id": execution.execution_id, "idempotency_key": key}, actor=actor,
                    runtime_session_id=runtime_session_id, agent_job_id=agent_job_id)
        result = self._write_runner.run(server_id=server_id, action=action, command=tool.command_for(action), timeout_seconds=tool.timeout_seconds)
        if not isinstance(result, WriteCommandResult):
            result = WriteCommandResult(**result)
        after_evidence = self._collect_evidence(
            plan=plan, execution_id=execution_id, server_id=server_id,
            service=action.target, phase="after",
        )
        after_ids = [after_evidence.evidence_id] if after_evidence is not None else []
        if not result.success:
            self._repository.update_execution(execution.execution_id, status=ExecutionStatus.FAILED.value, after_evidence_ids=after_ids,
                                               exit_status=result.exit_status, stdout=result.stdout, stderr=result.stderr,
                                               error=result.error or "write_execution_failed", completed_at=utc_now())
            self._repository.update_plan_status(plan_id, RemediationPlanStatus.ROLLBACK_REQUIRED.value,
                                                execution_status=ExecutionStatus.FAILED.value, rollback_status=RollbackStatus.REQUIRED.value)
            self._audit(plan, "execution_failed", {"execution_id": execution.execution_id, "error": result.error}, actor=actor,
                        runtime_session_id=runtime_session_id, agent_job_id=agent_job_id)
            return {"applied": False, "plan_id": plan_id, "execution_id": execution.execution_id, "blocked_reason": "execution_failed", "message": result.error or "Write execution failed."}
        if after_evidence is None:
            self._repository.update_execution(execution.execution_id, status=ExecutionStatus.FAILED.value, after_evidence_ids=[],
                                              exit_status=result.exit_status or 0, stdout=result.stdout, stderr=result.stderr,
                                              error="after_evidence_unavailable", completed_at=utc_now())
            self._repository.update_plan_status(plan_id, RemediationPlanStatus.ROLLBACK_REQUIRED.value,
                                                execution_status=ExecutionStatus.FAILED.value,
                                                rollback_status=RollbackStatus.REQUIRED.value)
            self._audit(plan, "after_evidence_failed", {"execution_id": execution.execution_id}, actor=actor,
                        runtime_session_id=runtime_session_id, agent_job_id=agent_job_id)
            return {"applied": False, "plan_id": plan_id, "execution_id": execution.execution_id,
                    "blocked_reason": "after_evidence_unavailable", "message": "Project-owned after Evidence could not be collected."}
        self._repository.update_execution(execution.execution_id, status=ExecutionStatus.SUCCEEDED.value, after_evidence_ids=after_ids,
                                          exit_status=result.exit_status or 0, stdout=result.stdout, stderr=result.stderr, completed_at=utc_now())
        verified, details = self._verify_state(server_id=server_id, action=action, expected_state=tool.expected_effect)
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
        return {"applied": True, "plan_id": plan_id, "execution_id": execution.execution_id,
                "verified": True, "idempotent": False, "before_evidence_ids": before_ids,
                "after_evidence_ids": after_ids}

    def rollback(self, *, plan_id: str, execution_id: str, actor: str | None = None, server_id: int | None = None) -> dict:
        """
        ينفذ إجراء التراجع المناسب ويتحقق من عودة حالة الخدمة.
        """
        plan = self._require_plan(plan_id)
        execution = self._repository.get_execution(execution_id)
        if execution is None or execution.plan_id != plan_id:
            return self._blocked(plan_id, "execution_not_found", "Execution does not belong to this plan.")
        if execution.status not in {ExecutionStatus.SUCCEEDED.value, ExecutionStatus.FAILED.value}:
            return self._blocked(plan_id, "execution_not_ready_for_rollback", "Execution is not in a state that permits operator rollback.")
        actions = [RemediationAction.from_dict(action) for action in (plan.proposed_actions or [])]
        if len(actions) != 1:
            return self._blocked(plan_id, "rollback_not_supported", "Rollback requires one registered action.")
        action = actions[0]
        tool = self._write_tools.get(action.action_type)
        if tool is None or server_id is None or plan.server_id != server_id:
            return self._blocked(plan_id, "rollback_policy_denied", "Rollback requires the registered reverse action and original server.")
        before_ids = list(execution.before_evidence_ids or [])
        if len(before_ids) != 1:
            return self._blocked(plan_id, "rollback_evidence_invalid", "Rollback requires exactly one project-owned before Evidence record.")
        before = self._repository.get_evidence(before_ids[0])
        if before is None or not self._evidence_belongs_to(before, plan_id=plan_id, execution_id=execution_id,
                                                          server_id=server_id, service=action.target):
            return self._blocked(plan_id, "rollback_evidence_invalid", "Before Evidence is missing, foreign, or has mismatched ownership.")
        reverse_action_type = self._resolve_state_aware_rollback(action, before.observed_state)
        if reverse_action_type is None:
            return self._blocked(plan_id, "rollback_not_supported", "This action has no true prior-state restoration path.")
        rollback_before = self._collect_evidence(
            plan=plan, execution_id=execution_id, server_id=server_id,
            service=action.target, phase="rollback_before",
        )
        if rollback_before is None or rollback_before.observed_state != tool.expected_effect:
            return self._blocked(plan_id, "rollback_state_mismatch", "Current state does not match the verified post-action state.")
        reverse = RemediationAction(action_type=reverse_action_type, target=action.target, action_id=f"rollback:{action.action_id or action.action_type}")
        reverse_tool = self._write_tools.resolve(reverse)
        result = self._write_runner.run(server_id=server_id, action=reverse, command=reverse_tool.command_for(reverse), timeout_seconds=reverse_tool.timeout_seconds)
        success = result.success if isinstance(result, WriteCommandResult) else bool(result.get("success"))
        rollback_after = self._collect_evidence(
            plan=plan, execution_id=execution_id, server_id=server_id,
            service=action.target, phase="rollback_after",
        )
        verified = rollback_after is not None and rollback_after.observed_state == before.observed_state
        if success:
            verified, verify_details = self._verify_state(
                server_id=server_id, action=reverse, expected_state=before.observed_state,
            )
        else:
            verify_details = {"expected": before.observed_state, "skipped": True}
        success = success and rollback_after is not None and verified
        rollback_status = RollbackStatus.SUCCEEDED.value if success else RollbackStatus.FAILED.value
        rollback = self._repository.create_rollback(
            rollback_id=str(uuid4()), execution_id=execution_id, status=rollback_status,
            before_evidence_ids=[rollback_before.evidence_id],
            after_evidence_ids=[rollback_after.evidence_id] if rollback_after is not None else [],
            details={"action_type": reverse.action_type, "error": getattr(result, "error", None),
                     "verification": verify_details, "original_before_state": before.observed_state},
        )
        self._repository.update_plan_status(plan_id, RemediationPlanStatus.ROLLBACK_SUCCEEDED.value if success else RemediationPlanStatus.ROLLBACK_FAILED.value,
                                            rollback_status=rollback_status)
        self._audit(plan, "rollback_succeeded" if success else "rollback_failed", {"rollback_id": rollback.rollback_id}, actor=actor)
        return {"rolled_back": success, "plan_id": plan_id, "rollback_id": rollback.rollback_id,
                "before_evidence_ids": [rollback_before.evidence_id],
                "after_evidence_ids": [rollback_after.evidence_id] if rollback_after is not None else []}
