"""
إدارة دورة معالجة المشكلة بعد التشخيص.

تنشئ الخدمة خطة قابلة للفحص، تتحقق منها في بيئة معزولة، تطلب الموافقة قبل
التغيير، تنفذ الخطة المعتمدة، وتتحقق من النتيجة أو تنفذ التراجع مع سجل تدقيق.
"""
from __future__ import annotations

from app.core.ports.remediation.service_state_evidence_collector import ServiceStateEvidenceCollector
from app.capabilities.remediation.execution.fallback_evidence_collector import FallbackEvidenceCollector
from app.capabilities.remediation.execution.fallback_verification_runner import FallbackVerificationRunner
from app.capabilities.remediation.execution.fallback_write_runner import FallbackWriteRunner
from app.core.ports.remediation.verification_runner import VerificationRunner
from app.core.ports.remediation.write_command_runner import WriteCommandRunner
from app.core.ports.remediation.remediation_repository import RemediationRepositoryPort
from app.core.policies.remediation_policy import RemediationPolicyEngine
from app.core.policies.remediation_risk import RemediationRiskClassifier
from app.core.policies.remediation_tools.named_write_tool_registry import NamedWriteToolRegistry
from app.core.policies.remediation_tools.factories import build_default_write_tool_registry
from app.capabilities.remediation.sandbox_runtime import NativeSandboxRuntime

from .planning import _RemediationPlanningMixin
from .sandbox import _RemediationSandboxMixin
from .approval import _RemediationApprovalMixin
from .execution import _RemediationExecutionMixin
from .query import _RemediationQueryMixin
from .audit_support import _RemediationAuditMixin
from .evidence_support import _RemediationEvidenceMixin
from .validation_support import _RemediationValidationMixin


class RemediationService(_RemediationPlanningMixin, _RemediationSandboxMixin, _RemediationApprovalMixin, _RemediationExecutionMixin, _RemediationQueryMixin, _RemediationEvidenceMixin, _RemediationAuditMixin, _RemediationValidationMixin):
    """
    ينسق اقتراح خطة المعالجة والتحقق والموافقة والتنفيذ والتراجع والتدقيق.
    """

    def __init__(
        self,
        *,
        repository: RemediationRepositoryPort,
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
        self._write_runner = write_runner or FallbackWriteRunner()
        self._verification_runner = verification_runner or FallbackVerificationRunner()
        self._evidence_collector = evidence_collector or FallbackEvidenceCollector()
        self._server_repository = server_repository
        self._sandbox_runtime = sandbox_runtime or NativeSandboxRuntime()
        self._issue_fingerprint_service = issue_fingerprint_service
