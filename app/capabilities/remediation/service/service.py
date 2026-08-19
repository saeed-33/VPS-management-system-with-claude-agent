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

from .planning import _RemediationPlanningMixin
from .sandbox import _RemediationSandboxMixin
from .approval import _RemediationApprovalMixin
from .execution import _RemediationExecutionMixin
from .query import _RemediationQueryMixin
from .support import _RemediationSupportMixin


class RemediationService(_RemediationPlanningMixin, _RemediationSandboxMixin, _RemediationApprovalMixin, _RemediationExecutionMixin, _RemediationQueryMixin, _RemediationSupportMixin):
    """
    ينسق اقتراح خطة المعالجة والتحقق والموافقة والتنفيذ والتراجع والتدقيق.
    """

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
        """
        يربط مستودعات الخطط والموافقات والتنفيذ والتدقيق والتشخيص ومكونات التحقق والمنفذين.
        """
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
