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


class _RemediationApprovalMixin:
    """ينظم مجموعة من عمليات خدمة المعالجة."""

    def request_approval(self, *, plan_id: str, expires_in_seconds: int = 3600, scope: dict | None = None):
        """
        ينشئ طلب موافقة قبل السماح بتطبيق خطة المعالجة.
        """
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
        """
        يقبل طلب الموافقة بعد التحقق من حالته وصلاحية الخطة.
        """
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
        """
        يرفض طلب الموافقة ويسجل سبب الرفض.
        """
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
        """
        ينقل موافقة منتهية إلى حالة الانتهاء ويمنع استخدامها.
        """
        approval = self._repository.expire_approval(approval_id)
        plan = self._require_plan(approval.plan_id)
        self._audit(plan, "approval_expired", {"approval_id": approval_id})
        return approval
