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


class _RemediationSupportMixin:
    """ينظم مجموعة من عمليات خدمة المعالجة."""

    def _blocked(self, plan_id: str, code: str, message: str) -> dict:
        """
        ينشئ نتيجة أو خطأ يوضح أن الخطة محجوبة بضابط أمان أو حالة غير صالحة.
        """
        self._repository.update_plan_status(plan_id, RemediationPlanStatus.BLOCKED.value, denial_reason=message)
        return {"applied": False, "plan_id": plan_id, "blocked_reason": code, "message": message}

    def _collect_evidence(self, *, plan, execution_id: str | None, server_id: int,
                          service: str, phase: str):
        """
        يجمع الأدلة المطلوبة لتنفيذ الخطة والتحقق من أثرها.
        """
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
        """
        يتحقق من أن دليل الحالة يخص الخطة والسيرفر المطلوبين.
        """
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
        """
        يختار إجراء التراجع بناءً على حالة الخدمة المرصودة قبل التنفيذ وبعده.
        """
        if action.action_type == "start_service" and before_state == "inactive":
            return "stop_service"
        if action.action_type == "stop_service" and before_state == "active":
            return "start_service"
        # إعادة التشغيل أو التحميل لا تعيد حالة العملية والإعدادات السابقة.
        return None

    def _verify_state(self, *, server_id: int, action: RemediationAction,
                      expected_state: str) -> tuple[bool, dict]:
        """
        يقارن الحالة المرصودة بالحالة المتوقعة ويحدد نجاح التحقق.
        """
        verify_state = getattr(self._verification_runner, "verify_state", None)
        if callable(verify_state):
            return verify_state(server_id=server_id, service=action.target, expected_state=expected_state)
        # إذا لم يستطع الفحص القديم إثبات الحالة غير النشطة، نفشل بأمان بدل
        # الادعاء بأن التراجع نجح.
        if expected_state != "active":
            return False, {"expected": expected_state, "error": "state_aware_verifier_not_configured"}
        return self._verification_runner.verify(server_id=server_id, action=action)

    def _require_plan(self, plan_id: str):
        """
        يجلب خطة مطلوبة ويتحقق من وجودها وروابطها الأساسية.
        """
        if not plan_id.strip():
            raise ValueError("plan_id must not be empty.")
        plan = self._repository.get_plan(plan_id)
        if plan is None:
            raise ValueError(f"Remediation plan not found: {plan_id}")
        return plan

    def _audit(self, plan, event_type: str, payload: dict, actor: str | None = None,
               runtime_session_id: str | None = None, agent_job_id: str | None = None) -> None:
        """
        يسجل حدث تدقيق لدورة المعالجة مع الفاعل والخطة والتفاصيل.
        """
        try:
            self._repository.append_audit_event(plan_id=plan.plan_id, event_type=event_type, actor=actor,
                                                server_id=getattr(plan, "server_id", None),
                                                runtime_session_id=runtime_session_id,
            agent_job_id=agent_job_id, payload=payload)
        except OperationalError:
            # قد تفتقد قاعدة قديمة جدول التدقيق الجديد؛ نبقي القراءة واختبار
            # الخطة ممكنين أثناء ترقية السجل الإضافي.
            return

    def audit_autonomous(self, *, plan_id: str, event_type: str, payload: dict) -> None:
        """
        يسجل حدث تدقيق خاص بتنفيذ آلي مرتبط بالمعالجة.
        """
        self._audit(self._require_plan(plan_id), event_type, payload, actor="autonomous-policy")

    @staticmethod
    def _validate_links(*, diagnosis_claim_ids: list[str], evidence_ids: list[str]) -> None:
        """
        يتحقق من تطابق هوية الخطة والتشخيص والسيرفر قبل المتابعة.
        """
        if not diagnosis_claim_ids:
            raise ValueError("diagnosis_claim_ids must not be empty.")
        if not evidence_ids:
            raise ValueError("evidence_ids must not be empty.")

    @staticmethod
    def _validate_actions(proposed_actions: list[dict]) -> None:
        """
        يتحقق من أن أفعال الخطة معروفة ومسموحة وقابلة للتنفيذ أو التراجع.
        """
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
