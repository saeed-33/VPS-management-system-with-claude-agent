from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from sqlalchemy.exc import OperationalError

from app.capabilities.remediation.execution import (
    ServiceStateEvidenceCollector,
    ServiceStateObservation,
    UnavailableEvidenceCollector,
    UnavailableVerificationRunner,
    UnavailableWriteRunner,
    VerificationRunner,
    WriteCommandResult,
    WriteCommandRunner,
)
from app.capabilities.remediation.sandbox_runtime import NativeSandboxRuntime
from app.core.contracts.sandbox_validation import (
    SandboxRuntimeCheck,
    SandboxTarget,
    SandboxValidationStatus,
)
from app.core.policies.sandbox_validation import validate_sandbox_target
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
from app.core.contracts.autonomous_remediation import AutonomousAuthorizationStatus
from app.core.contracts.autonomous_remediation import AutonomousAuthorization
from app.core.contracts.analysis import ErrorClassification
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
        evidence_collector: ServiceStateEvidenceCollector | None = None,
        server_repository=None,
        sandbox_runtime=None,
        issue_fingerprint_service=None,
    ) -> None:
        self._repository = repository
        self._automatic_remediation_allowed = automatic_remediation_allowed
        self._write_tools = write_tool_registry or build_default_write_tool_registry()
        self._risk_classifier = RemediationRiskClassifier(self._write_tools)
        self._policy = RemediationPolicyEngine(automatic_remediation_allowed=automatic_remediation_allowed)
        self._write_runner = write_runner or UnavailableWriteRunner()
        self._verification_runner = verification_runner or UnavailableVerificationRunner()
        self._evidence_collector = evidence_collector or UnavailableEvidenceCollector()
        self._server_repository = server_repository
        self._sandbox_runtime = sandbox_runtime or NativeSandboxRuntime()
        self._issue_fingerprint_service = issue_fingerprint_service

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
                    plan_id: str | None = None, server_id: int | None = None,
                    error_classification: str | None = None):
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
        metadata = {
            "production_application_allowed": False,
            "automatic_remediation_allowed": self._automatic_remediation_allowed,
            "registered_actions": registered,
        }
        if error_classification is not None:
            metadata["error_classification"] = ErrorClassification(
                error_classification
            ).value
        if self._issue_fingerprint_service is not None:
            trusted_issue_fingerprint = self._issue_fingerprint_service.derive(investigation_id)
            if trusted_issue_fingerprint:
                metadata["issue_fingerprint"] = trusted_issue_fingerprint

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
                metadata=metadata,
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

    def collect_service_evidence(self, *, plan_id: str, server_id: int,
                                 service: str, phase: str = "preflight"):
        plan = self._require_plan(plan_id)
        self._write_tools.require("start_service").validate(
            RemediationAction(action_type="start_service", target=service)
        )
        evidence = self._collect_evidence(
            plan=plan, execution_id=None, server_id=server_id,
            service=service, phase=phase,
        )
        if evidence is None:
            raise ValueError("Project-owned service-state Evidence could not be collected.")
        return evidence

    def list_plans(self, *, limit: int = 100, status: str | None = None):
        return self._repository.list_plans(limit=limit, status=status)

    def get_sandbox_result(self, result_id: str | None = None, *, plan_id: str | None = None):
        if result_id is not None:
            return self._repository.get_sandbox_result(result_id)
        if plan_id is not None:
            return self._repository.get_latest_sandbox_result_for_plan(plan_id)
        raise ValueError("result_id or plan_id is required.")

    def get_sandbox_validation(self, validation_id: str | None = None, *, plan_id: str | None = None):
        if validation_id is not None:
            return self._repository.get_sandbox_validation(validation_id)
        if plan_id is not None:
            return self._repository.get_latest_sandbox_validation(plan_id)
        raise ValueError("validation_id or plan_id is required.")

    def validate_in_isolated_sandbox(self, *, plan_id: str, target_server_id: int,
                                     target_server_name: str, target_service: str,
                                     runtime_check: SandboxRuntimeCheck | None = None):
        plan = self._require_plan(plan_id)
        actions = [RemediationAction.from_dict(item) for item in (plan.proposed_actions or [])]
        validation_id = str(uuid4())
        started_at = utc_now()
        base = {
            "validation_id": validation_id,
            "plan_id": plan.plan_id,
            "plan_fingerprint": plan.plan_fingerprint,
            "server_id": target_server_id,
            "server_name": target_server_name,
            "service": target_service,
            "action_type": actions[0].action_type if len(actions) == 1 else "unknown",
            "action_parameters": actions[0].parameters if len(actions) == 1 else {},
            "expected_state": "unknown",
            "observed_state": None,
            "before_evidence_ids": [],
            "after_evidence_ids": [],
            "verification_status": "inconclusive",
            "status": SandboxValidationStatus.ERROR.value,
            "started_at": started_at,
            "finished_at": None,
            "failure_reason": None,
            "validation_metadata": {"runtime": "claude-native-sandbox"},
        }
        if len(actions) != 1:
            base["failure_reason"] = "exactly_one_registered_action_required"
            return self._finish_sandbox_validation(plan, base, "sandbox_validation_failed")
        action = actions[0]
        try:
            tool = self._write_tools.resolve(action)
            base["expected_state"] = tool.expected_effect
            if action.target != target_service:
                raise ValueError("Sandbox service must match the registered plan action target.")
            if self._server_repository is None:
                raise ValueError("Sandbox target repository is unavailable.")
            server = self._server_repository.get_by_id(target_server_id)
            target = SandboxTarget(target_server_id, target_server_name, target_service, server.description if server else "")
            validate_sandbox_target(server=server, target=target)
            check = runtime_check or self._sandbox_runtime.check()
            if not check.available:
                raise ValueError(f"native_sandbox_unavailable:{check.reason}")
            base["validation_metadata"] = {
                "runtime": check.runtime,
                "runtime_available": check.available,
                "runtime_evidence": check.evidence,
            }
            self._audit(plan, "sandbox_validation_started", {"validation_id": validation_id})
            before = self._collect_evidence(plan=plan, execution_id=validation_id, server_id=target_server_id,
                                             service=target_service, phase="sandbox_before")
            if before is None or before.observed_state not in {"active", "inactive"}:
                raise ValueError("sandbox_before_evidence_unavailable")
            base["before_evidence_ids"] = [before.evidence_id]
            base["status"] = SandboxValidationStatus.RUNNING.value
            self._audit(plan, "sandbox_before_evidence_collected", {"validation_id": validation_id})
            rollback_type = self._resolve_state_aware_rollback(action, before.observed_state)
            if rollback_type is None:
                raise ValueError("sandbox_action_has_no_safe_restoration_path")
            self._audit(plan, "sandbox_action_started", {"validation_id": validation_id, "action": action.action_type})
            result = self._write_runner.run(server_id=target_server_id, action=action,
                                            command=tool.command_for(action), timeout_seconds=tool.timeout_seconds)
            if not isinstance(result, WriteCommandResult):
                result = WriteCommandResult(**result)
            after = self._collect_evidence(plan=plan, execution_id=validation_id, server_id=target_server_id,
                                           service=target_service, phase="sandbox_after")
            if after is None:
                raise ValueError("sandbox_after_evidence_unavailable")
            base["after_evidence_ids"] = [after.evidence_id]
            base["observed_state"] = after.observed_state
            self._audit(plan, "sandbox_after_evidence_collected", {"validation_id": validation_id})
            if not result.success:
                raise ValueError(result.error or "sandbox_action_failed")
            verified, details = self._verify_state(server_id=target_server_id, action=action, expected_state=tool.expected_effect)
            base["validation_metadata"]["verification"] = details
            base["verification_status"] = "verified" if verified else "failed"
            if not verified or after.observed_state != tool.expected_effect:
                self._audit(plan, "sandbox_verification_failed", {"validation_id": validation_id})
                raise ValueError("sandbox_verification_mismatch")
            self._audit(plan, "sandbox_verification_passed", {"validation_id": validation_id})
            reverse = RemediationAction(action_type=rollback_type, target=action.target, action_id=f"sandbox-restore:{action.action_id or action.action_type}")
            reverse_tool = self._write_tools.resolve(reverse)
            restore = self._write_runner.run(server_id=target_server_id, action=reverse,
                                             command=reverse_tool.command_for(reverse), timeout_seconds=reverse_tool.timeout_seconds)
            if not isinstance(restore, WriteCommandResult):
                restore = WriteCommandResult(**restore)
            final = self._collect_evidence(plan=plan, execution_id=validation_id, server_id=target_server_id,
                                           service=target_service, phase="sandbox_restore")
            base["validation_metadata"]["restored_state"] = final.observed_state if final else None
            if not restore.success or final is None or final.observed_state != before.observed_state:
                raise ValueError("sandbox_cleanup_restoration_failed")
            base["validation_metadata"]["cleanup_evidence_id"] = final.evidence_id
            base["status"] = SandboxValidationStatus.PASSED.value
            self._audit(plan, "sandbox_validation_passed", {"validation_id": validation_id})
        except Exception as exc:
            base["status"] = SandboxValidationStatus.FAILED.value
            base["failure_reason"] = str(exc)
            self._audit(plan, "sandbox_validation_failed", {"validation_id": validation_id, "reason": str(exc)})
        return self._finish_sandbox_validation(plan, base, None)

    def _finish_sandbox_validation(self, plan, data: dict, event_type: str | None):
        data["finished_at"] = utc_now()
        model = self._repository.finalize_sandbox_validation(**data)
        if data.get("status") == SandboxValidationStatus.PASSED.value and model.status != SandboxValidationStatus.PASSED.value:
            event = "sandbox_validation_stale" if model.status == SandboxValidationStatus.STALE.value else "sandbox_validation_failed"
            self._audit(plan, event, {"validation_id": model.validation_id, "reason": model.failure_reason})
        if event_type:
            self._audit(plan, event_type, {"validation_id": model.validation_id})
        return model

    def request_approval(self, *, plan_id: str, expires_in_seconds: int = 3600, scope: dict | None = None):
        plan = self._require_plan(plan_id)
        validation = self._repository.get_latest_sandbox_validation(plan_id)
        if validation is None:
            raise ValueError("Sandbox validation must pass before approval can be requested.")
        if validation.plan_fingerprint != plan.plan_fingerprint:
            self._repository.update_sandbox_validation(validation.validation_id, status=SandboxValidationStatus.STALE.value,
                                                       failure_reason="plan_fingerprint_changed")
            self._audit(plan, "sandbox_validation_stale", {"validation_id": validation.validation_id})
            raise ValueError("Sandbox validation is stale for the current plan fingerprint.")
        if validation.status != SandboxValidationStatus.PASSED.value:
            raise ValueError("Sandbox validation must pass before approval can be requested.")
        if validation.server_id != plan.server_id or validation.action_type != RemediationAction.from_dict(plan.proposed_actions[0]).action_type:
            raise ValueError("Sandbox validation target/action does not belong to this plan.")
        if plan.status not in {RemediationPlanStatus.SANDBOX_PASSED.value, RemediationPlanStatus.PROPOSED.value}:
            raise ValueError("Plan is not eligible for approval.")
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
                       agent_job_id: str | None = None,
                       autonomous_authorization: AutonomousAuthorization | None = None) -> dict:
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
            # Legacy callers cannot self-approve. Preserve the historical
            # response shape while requiring the new persisted approval path.
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

    def list_audit_events(self, plan_id: str):
        return self._repository.list_audit_events(plan_id)

    def list_all_audit_events(
        self, *, plan_id: str | None = None, event_type: str | None = None, limit: int = 100
    ):
        return self._repository.list_all_audit_events(
            plan_id=plan_id, event_type=event_type, limit=min(max(limit, 1), 500)
        )

    def recover_interrupted_executions(self) -> int:
        return self._repository.mark_interrupted_executions()

    def _blocked(self, plan_id: str, code: str, message: str) -> dict:
        self._repository.update_plan_status(plan_id, RemediationPlanStatus.BLOCKED.value, denial_reason=message)
        return {"applied": False, "plan_id": plan_id, "blocked_reason": code, "message": message}

    def _collect_evidence(self, *, plan, execution_id: str | None, server_id: int,
                          service: str, phase: str):
        try:
            observation = self._evidence_collector.collect(server_id=server_id, service=service)
        except Exception:
            return None
        if not isinstance(observation, ServiceStateObservation):
            return None
        if observation.state == "unknown":
            return None
        evidence = self._repository.create_evidence(
            evidence_id=str(uuid4()), plan_id=plan.plan_id, execution_id=execution_id,
            server_id=server_id, service=service, phase=phase,
            observed_state=observation.state,
            metadata={"stdout": observation.stdout, "stderr": observation.stderr,
                      "exit_status": observation.exit_status, "error": observation.error,
                      **dict(observation.metadata)},
        )
        return evidence

    @staticmethod
    def _evidence_belongs_to(evidence, *, plan_id: str, execution_id: str,
                             server_id: int, service: str) -> bool:
        return (
            evidence.plan_id == plan_id
            and evidence.execution_id == execution_id
            and evidence.server_id == server_id
            and evidence.service == service
            and evidence.phase == "before"
            and evidence.observed_state in {"active", "inactive"}
        )

    @staticmethod
    def _resolve_state_aware_rollback(action: RemediationAction, before_state: str) -> str | None:
        if action.action_type == "start_service" and before_state == "inactive":
            return "stop_service"
        if action.action_type == "stop_service" and before_state == "active":
            return "start_service"
        # Restart and reload do not restore the prior process/config state.
        return None

    def _verify_state(self, *, server_id: int, action: RemediationAction,
                      expected_state: str) -> tuple[bool, dict]:
        verify_state = getattr(self._verification_runner, "verify_state", None)
        if callable(verify_state):
            return verify_state(server_id=server_id, service=action.target, expected_state=expected_state)
        # Legacy adapters only know how to verify active. Fail closed for an
        # inactive expected state rather than claiming a false rollback.
        if expected_state != "active":
            return False, {"expected": expected_state, "error": "state_aware_verifier_not_configured"}
        return self._verification_runner.verify(server_id=server_id, action=action)

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

    def audit_autonomous(self, *, plan_id: str, event_type: str, payload: dict) -> None:
        """Append a Phase 7 event through the existing remediation audit sink."""
        self._audit(self._require_plan(plan_id), event_type, payload, actor="autonomous-policy")

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
