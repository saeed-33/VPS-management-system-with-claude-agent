"""
إدارة دورة معالجة المشكلة بعد التشخيص.

تنشئ الخدمة خطة قابلة للفحص، تتحقق منها في بيئة معزولة، تطلب الموافقة قبل
التغيير، تنفذ الخطة المعتمدة، وتتحقق من النتيجة أو تنفذ التراجع مع سجل تدقيق.
"""
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from sqlalchemy.exc import OperationalError

from app.capabilities.remediation.execution.service_state_evidence_collector import ServiceStateEvidenceCollector
from app.capabilities.remediation.execution.service_state_observation import ServiceStateObservation
from app.capabilities.remediation.execution.unavailable_evidence_collector import UnavailableEvidenceCollector
from app.capabilities.remediation.execution.unavailable_verification_runner import UnavailableVerificationRunner
from app.capabilities.remediation.execution.unavailable_write_runner import UnavailableWriteRunner
from app.capabilities.remediation.execution.verification_runner import VerificationRunner
from app.capabilities.remediation.execution.write_command_result import WriteCommandResult
from app.capabilities.remediation.execution.write_command_runner import WriteCommandRunner
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
from app.infrastructure.database.repositories.remediation_repository.repository import RemediationRepository


class _RemediationSandboxMixin:
    """ينظم مجموعة من عمليات خدمة المعالجة."""

    def validate_in_isolated_sandbox(self, *, plan_id: str, target_server_id: int,
                                     target_server_name: str, target_service: str,
                                     runtime_check: SandboxRuntimeCheck | None = None):
        """
        ينفذ التحقق المعزول ويسجل جاهزية البيئة ونتيجة الأفعال المقترحة.
        """
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
        """
        يحدّث سجل التحقق المعزول بنتيجة النجاح أو الفشل والتفاصيل.
        """
        data["finished_at"] = utc_now()
        model = self._repository.finalize_sandbox_validation(**data)
        if data.get("status") == SandboxValidationStatus.PASSED.value and model.status != SandboxValidationStatus.PASSED.value:
            event = "sandbox_validation_stale" if model.status == SandboxValidationStatus.STALE.value else "sandbox_validation_failed"
            self._audit(plan, event, {"validation_id": model.validation_id, "reason": model.failure_reason})
        if event_type:
            self._audit(plan, event_type, {"validation_id": model.validation_id})
        return model
