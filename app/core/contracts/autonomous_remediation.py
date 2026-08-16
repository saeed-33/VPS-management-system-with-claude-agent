"""عقود قرار المعالجة الذاتية وحدود السماح بتنفيذها على السيرفر."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class AutonomousPolicyStatus(StrEnum):
    """
    حالات سياسة المعالجة الذاتية من التفعيل حتى التعليق الوقائي.
    """
    ENABLED = "enabled"
    DISABLED = "disabled"
    SUSPENDED = "suspended"


class AutonomousDecisionOutcome(StrEnum):
    """
    النتيجة العملية لتقييم أهلية المعالجة الذاتية.
    """
    AUTO_EXECUTE = "auto_execute"
    REQUIRE_HUMAN_APPROVAL = "require_human_approval"
    DENY = "deny"


class AutonomousAuthorizationStatus(StrEnum):
    """
    حالة التفويض الذي يربط قرار السياسة بخطة تغيير محددة.
    """
    VALID = "valid"
    CONSUMED = "consumed"
    STALE = "stale"
    EXPIRED = "expired"
    REVOKED = "revoked"


class AutonomousSuspensionReason(StrEnum):
    """
    سبب إيقاف المعالجة الذاتية بعد فشل أو مخالفة سلامة أو قرار مشغل.
    """
    EXECUTION_FAILURE = "execution_failure"
    VERIFICATION_FAILURE = "verification_failure"
    ROLLBACK_FAILURE = "rollback_failure"
    CONSECUTIVE_FAILURE_THRESHOLD = "consecutive_failure_threshold"
    OPERATOR_SUSPENSION = "operator_suspension"
    SAFETY_VIOLATION = "safety_violation"


class AutonomousDecisionReasonCode(StrEnum):
    """
    رموز تشرح لماذا سمحت السياسة بالمعالجة أو طلبت موافقة أو منعتها.
    """
    POLICY_MATCH = "policy_match"
    POLICY_DISABLED = "policy_disabled"
    POLICY_SUSPENDED = "policy_suspended"
    GLOBAL_AUTONOMY_DISABLED = "global_autonomy_disabled"
    ACTION_NOT_AUTONOMOUS_ALLOWLISTED = "action_not_autonomous_allowlisted"
    TARGET_NOT_ALLOWED = "target_not_allowed"
    SERVER_NOT_ALLOWED = "server_not_allowed"
    RISK_TOO_HIGH = "risk_too_high"
    CONFIDENCE_INSUFFICIENT = "confidence_insufficient"
    EVIDENCE_INCOMPLETE = "evidence_incomplete"
    HISTORICAL_SUCCESSES_INSUFFICIENT = "historical_successes_insufficient"
    HISTORICAL_FAILURE_RATE_TOO_HIGH = "historical_failure_rate_too_high"
    SANDBOX_MISSING = "sandbox_missing"
    SANDBOX_FAILED = "sandbox_failed"
    SANDBOX_STALE = "sandbox_stale"
    SANDBOX_FINGERPRINT_MISMATCH = "sandbox_fingerprint_mismatch"
    ROLLBACK_UNAVAILABLE = "rollback_unavailable"
    COOLDOWN_ACTIVE = "cooldown_active"
    HOURLY_RATE_LIMIT_EXCEEDED = "hourly_rate_limit_exceeded"
    DAILY_RATE_LIMIT_EXCEEDED = "daily_rate_limit_exceeded"
    CONSECUTIVE_FAILURE_LIMIT_EXCEEDED = "consecutive_failure_limit_exceeded"
    EXECUTION_ALREADY_COMPLETED = "execution_already_completed"
    EXECUTION_IN_PROGRESS = "execution_in_progress"
    AUTHORIZATION_STALE = "authorization_stale"
    HARD_DENY = "hard_deny"
    AMBIGUOUS_POLICY_MATCH = "ambiguous_policy_match"
    NO_POLICY_MATCH = "no_policy_match"
    ISSUE_FINGERPRINT_MISSING = "issue_fingerprint_missing"
    DANGEROUS_ERROR_CLASSIFICATION = "dangerous_error_classification"
    SENSITIVE_ERROR_CLASSIFICATION = "sensitive_error_classification"


V1_AUTONOMOUS_ACTIONS = frozenset({"start_service"})
V1_AUTONOMOUS_RISK_CEILING = "low"


@dataclass(slots=True, frozen=True)
class AutonomousRemediationPolicy:
    """
    سياسة تحدد متى يمكن تنفيذ علاج معين تلقائيًا لسيرفر محدد.

    تجمع السياسة الخطر والثقة والأدلة والاختبار والتراجع وحدود المعدل والتاريخ،
    حتى لا يتحول تشخيص واحد إلى صلاحية عامة لتغيير السيرفرات.
    """
    policy_id: str
    name: str
    description: str
    status: AutonomousPolicyStatus
    version: int
    issue_fingerprint: str
    allowed_action_type: str
    allowed_target_pattern: str
    maximum_risk: str = "low"
    minimum_confidence: float = 0.0
    required_evidence: tuple[str, ...] = ("diagnosis", "plan", "sandbox_before", "sandbox_after", "verification")
    minimum_success_count: int = 0
    maximum_failure_rate: float = 0.0
    maximum_rollback_failure_rate: float = 0.0
    allowed_server_ids: tuple[int, ...] = ()
    allowed_server_tags: tuple[str, ...] = ()
    sandbox_required: bool = True
    sandbox_max_age_seconds: int = 3600
    rollback_required: bool = True
    cooldown_seconds: int = 0
    max_executions_per_hour: int = 1
    max_executions_per_day: int = 3
    max_consecutive_failures: int = 1
    auto_suspend_on_failure: bool = True
    created_by: str = "admin"
    updated_by: str = "admin"
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """يتحقق من هوية السياسة وإصدارتها وحدود الثقة والفشل والتكرار."""
        if not self.policy_id.strip() or not self.name.strip():
            raise ValueError("policy_id and name must not be empty.")
        if self.version < 1:
            raise ValueError("policy version must be >= 1.")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("minimum_confidence must be between 0 and 1.")
        if not 0 <= self.maximum_failure_rate <= 1:
            raise ValueError("maximum_failure_rate must be between 0 and 1.")
        if not 0 <= self.maximum_rollback_failure_rate <= 1:
            raise ValueError("maximum_rollback_failure_rate must be between 0 and 1.")
        for value in (self.sandbox_max_age_seconds, self.max_executions_per_hour, self.max_executions_per_day, self.max_consecutive_failures):
            if value < 1:
                raise ValueError("policy limits must be positive.")


@dataclass(slots=True, frozen=True)
class AutonomousHistorySnapshot:
    """
    ملخص تاريخي لنجاح وفشل معالجة نفس المشكلة والفعل والهدف.

    تستخدمه السياسة لمعرفة هل يملك العلاج سجل نجاح كافيًا وهل تجاوز معدل الفشل
    أو فشل التراجع الحد الذي يوقف التنفيذ الذاتي.
    """
    issue_fingerprint: str
    action_type: str
    target: str
    supervised_execution_count: int = 0
    successful_execution_count: int = 0
    failed_execution_count: int = 0
    verified_success_count: int = 0
    verification_failure_count: int = 0
    rollback_required_count: int = 0
    rollback_success_count: int = 0
    rollback_failure_count: int = 0
    autonomous_execution_count: int = 0
    autonomous_success_count: int = 0
    autonomous_failure_count: int = 0
    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None

    @property
    def success_rate(self) -> float:
        """يحسب نسبة النجاحات المتحققة من إجمالي التنفيذات المراقبة."""
        return self.verified_success_count / self.supervised_execution_count if self.supervised_execution_count else 0.0

    @property
    def failure_rate(self) -> float:
        """يحسب نسبة التنفيذات الفاشلة التي يجب أن تؤثر على قرار السياسة."""
        return self.failed_execution_count / self.supervised_execution_count if self.supervised_execution_count else 0.0

    @property
    def rollback_failure_rate(self) -> float:
        """يحسب نسبة عمليات التراجع الفاشلة بين الحالات التي احتاجت تراجعًا."""
        return self.rollback_failure_count / self.rollback_required_count if self.rollback_required_count else 0.0


@dataclass(slots=True, frozen=True)
class AutonomousPolicyDecision:
    """
    سجل قرار سياسة قابل للمراجعة يشرح مآل المعالجة الذاتية وأسبابه.
    """
    decision_id: str
    outcome: AutonomousDecisionOutcome
    reason_codes: tuple[str, ...]
    human_readable_reasons: tuple[str, ...]
    policy_id: str | None = None
    policy_version: int | None = None
    plan_id: str | None = None
    plan_fingerprint: str | None = None
    issue_fingerprint: str | None = None
    server_id: int | None = None
    action_type: str | None = None
    target: str | None = None
    evaluated_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AutonomousAuthorization:
    """
    تفويض قصير العمر يثبت أن خطة بعينها اجتازت قرار السياسة والاختبار.

    يربط التفويض الخطة وبصمتها والسيرفر والفعل ونتيجة sandbox، ويمكن استهلاكه
    مرة واحدة قبل التنفيذ.
    """
    authorization_id: str
    token: str
    status: AutonomousAuthorizationStatus
    policy_id: str
    policy_version: int
    decision_id: str
    plan_id: str
    plan_fingerprint: str
    server_id: int
    action_type: str
    target: str
    sandbox_validation_id: str
    issued_at: datetime
    expires_at: datetime
    consumed_at: datetime | None = None


@dataclass(slots=True, frozen=True)
class AutonomousExecutionReservation:
    """
    حجز يمنع تنفيذ خطة المعالجة الذاتية نفسها بالتوازي أو التكرار.
    """
    reservation_id: str
    idempotency_key: str
    status: str
    policy_id: str
    plan_id: str
    authorization_id: str | None = None
    execution_id: str | None = None
    owner_token: str | None = None


@dataclass(slots=True, frozen=True)
class AutonomousPolicyCandidate:
    """
    مرشح سياسة مع إحصاءات التاريخ التي استخدمت في التقييم.
    """
    issue_fingerprint: str
    action_type: str
    target: str
    execution_count: int
    verified_success_count: int
    failure_count: int
    rollback_failure_count: int
    success_rate: float
    reason_codes: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class AutonomousEvaluationContext:
    """
    كل المعطيات التي تحتاجها سياسة المعالجة الذاتية لاتخاذ قرار آمن.

    يجمع السياق التشخيص والخطة ونتيجة sandbox والتاريخ والحدود الزمنية وحالة
    التنفيذ، حتى يكون القرار قابلًا لإعادة الفحص قبل الأثر الفعلي.
    """
    global_enabled: bool
    now: datetime
    policy: AutonomousRemediationPolicy | None
    plan_id: str
    plan_fingerprint: str
    issue_fingerprint: str
    server_id: int | None
    action_type: str
    target: str
    risk: str
    confidence: float
    diagnosis_evidence_valid: bool
    plan_evidence_valid: bool
    sandbox: Any | None
    history: AutonomousHistorySnapshot
    last_execution_at: datetime | None = None
    hourly_execution_count: int = 0
    daily_execution_count: int = 0
    consecutive_failures: int = 0
    execution_completed: bool = False
    execution_in_progress: bool = False
    plan_ready: bool = True
    ambiguous_policy_match: bool = False
    sandbox_evidence_valid: bool = False
    error_classification: str | None = None
