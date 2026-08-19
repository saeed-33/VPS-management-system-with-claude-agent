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


class _RemediationQueryMixin:
    """ينظم مجموعة من عمليات خدمة المعالجة."""

    def get_plan(self, plan_id: str):
        """
        يجلب خطة معالجة ويرفع خطأ عند عدم وجودها.
        """
        return self._repository.get_plan(plan_id)

    def get_approval(self, approval_id: str | None = None, *, plan_id: str | None = None):
        """
        يجلب طلب الموافقة المرتبط بالخطة.
        """
        return self._repository.get_approval(approval_id, plan_id=plan_id)

    def get_latest_execution(self, plan_id: str):
        """
        يعيد آخر تنفيذ مسجل لخطة المعالجة.
        """
        return self._repository.get_latest_execution_for_plan(plan_id)

    def collect_service_evidence(self, *, plan_id: str, server_id: int,
                                 service: str, phase: str = "preflight"):
        """
        يجمع دليل حالة الخدمة من السيرفر قبل التنفيذ أو بعده.
        """
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
        """
        يعرض خطط المعالجة مع المرشحات الإدارية المتاحة.
        """
        return self._repository.list_plans(limit=limit, status=status)

    def get_sandbox_result(self, result_id: str | None = None, *, plan_id: str | None = None):
        """
        يجلب نتيجة اختبار الخطة في البيئة المعزولة.
        """
        if result_id is not None:
            return self._repository.get_sandbox_result(result_id)
        if plan_id is not None:
            return self._repository.get_latest_sandbox_result_for_plan(plan_id)
        raise ValueError("result_id or plan_id is required.")

    def get_sandbox_validation(self, validation_id: str | None = None, *, plan_id: str | None = None):
        """
        يجلب سجل التحقق المعزول المرتبط بالخطة.
        """
        if validation_id is not None:
            return self._repository.get_sandbox_validation(validation_id)
        if plan_id is not None:
            return self._repository.get_latest_sandbox_validation(plan_id)
        raise ValueError("validation_id or plan_id is required.")

    def list_audit_events(self, plan_id: str):
        """
        يعرض أحداث التدقيق الخاصة بخطة معالجة معينة.
        """
        return self._repository.list_audit_events(plan_id)

    def list_all_audit_events(
        self, *, plan_id: str | None = None, event_type: str | None = None, limit: int = 100
    ):
        """
        يعرض أحداث التدقيق عبر خطط المعالجة مع المرشحات.
        """
        return self._repository.list_all_audit_events(
            plan_id=plan_id, event_type=event_type, limit=min(max(limit, 1), 500)
        )

    def recover_interrupted_executions(self) -> int:
        """
        يعالج تنفيذات توقفت أثناء العمل ويحدث حالتها بما يمنع فقدان الأثر.
        """
        return self._repository.mark_interrupted_executions()
