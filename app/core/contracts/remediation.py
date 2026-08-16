"""عقود خطة المعالجة، الموافقة، التنفيذ، والتحقق من أثر التغيير."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RemediationRisk(StrEnum):
    """
    مستوى الخطر المتوقع من تغيير مقترح على السيرفر.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# هذا هو اسم مستوى الخطر المستخدم في رحلة المعالجة، ويبقى الاسم القديم
# كمرجع توافق للسجلات والطلبات السابقة.
RiskLevel = RemediationRisk


class RemediationPlanStatus(StrEnum):
    """
    انتقالات خطة المعالجة من الاقتراح حتى النجاح أو الفشل أو التراجع.
    """
    PROPOSED = "proposed"
    SANDBOX_PASSED = "sandbox_passed"
    SANDBOX_FAILED = "sandbox_failed"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    VERIFICATION_PENDING = "verification_pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLBACK_REQUIRED = "rollback_required"
    ROLLBACK_SUCCEEDED = "rollback_succeeded"
    ROLLBACK_FAILED = "rollback_failed"
    CANCELLED = "cancelled"
    NO_SOLUTION_FOUND = "no_solution_found"
    APPLIED = "applied"  # historical terminal value
    BLOCKED = "blocked"


class ApprovalStatus(StrEnum):
    """
    حالات موافقة المشغل على خطة تغيير محددة.
    """
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ExecutionStatus(StrEnum):
    """
    حالات التنفيذ الفعلي للخطة بعد اجتياز الموافقة والسياسة.
    """
    CLAIMED = "claimed"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"


class VerificationStatus(StrEnum):
    """
    نتيجة فحص حالة السيرفر بعد تطبيق التغيير.
    """
    VERIFIED = "verified"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


class RollbackStatus(StrEnum):
    """
    حالات التراجع عندما لا يثبت التحقق نجاح المعالجة.
    """
    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class PolicyDecision(StrEnum):
    """
    مآل فحص سياسة المعالجة قبل السماح بالانتقال التالي.
    """
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    REQUIRE_ADDITIONAL_VALIDATION = "require_additional_validation"


def _canonical_json(value: Any) -> str:
    """
    يحول قيمة الخطة إلى JSON ثابت يصلح لبناء بصمة قابلة للمقارنة.

    يضمن ترتيب المفاتيح والشكل الموحد أن تعرف الخدمة هل تغيرت الخطة فعلًا قبل
    قبول موافقة أو تفويض قديم.
    """
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


@dataclass(slots=True, frozen=True)
class RemediationAction:
    """
    فعل واحد داخل خطة المعالجة مع هدفه وخطره وشروط التحقق والتراجع.

    يصف العقد ما سيحدث، لكنه لا يمنح الإذن بتنفيذه ولا يقبل نص shell حرًا.
    """

    action_type: str
    target: str
    parameters: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    expected_effect: str = ""
    risk_level: str = RemediationRisk.MEDIUM.value
    requires_approval: bool = True
    rollback_supported: bool = False
    verification_strategy: str = ""
    evidence_requirements: tuple[str, ...] = ()
    action_id: str | None = None

    def __post_init__(self) -> None:
        """يتحقق من وجود نوع وهدف ومن أن مستوى الخطر معروف للنظام."""
        if not self.action_type.strip():
            raise ValueError("action_type must not be empty.")
        if not self.target.strip():
            raise ValueError("target must not be empty.")
        if self.risk_level not in {item.value for item in RemediationRisk}:
            raise ValueError("risk_level is invalid.")

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RemediationAction":
        """
        ينشئ فعل معالجة من تمثيل قادم من خطة أو سجل قديم.

        يوحد أسماء الحقول القديمة والجديدة ويحول متطلبات الأدلة إلى مجموعة
        ثابتة قبل تطبيق تحقق العقد.
        """
        if not isinstance(value, dict):
            raise ValueError("remediation actions must be objects.")
        action_type = str(
            value.get("action_type")
            or value.get("tool")
            or value.get("type")
            or "legacy"
        )
        target = str(value.get("target") or value.get("service") or "legacy")
        evidence = value.get("evidence_requirements", ())
        if not isinstance(evidence, (list, tuple)):
            raise ValueError("evidence_requirements must be a list.")
        return cls(
            action_type=action_type,
            target=target,
            parameters=dict(value.get("parameters") or {}),
            reason=str(value.get("reason") or value.get("description") or ""),
            expected_effect=str(value.get("expected_effect") or ""),
            risk_level=str(value.get("risk_level") or RemediationRisk.MEDIUM.value),
            requires_approval=bool(value.get("requires_approval", True)),
            rollback_supported=bool(value.get("rollback_supported", False)),
            verification_strategy=str(value.get("verification_strategy") or ""),
            evidence_requirements=tuple(str(item) for item in evidence),
            action_id=(str(value["id"]) if value.get("id") is not None else None),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        يحول فعل المعالجة إلى بيانات قابلة للحفظ أو الإرسال إلى واجهة الإدارة.
        """
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "target": self.target,
            "parameters": dict(self.parameters),
            "reason": self.reason,
            "expected_effect": self.expected_effect,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
            "rollback_supported": self.rollback_supported,
            "verification_strategy": self.verification_strategy,
            "evidence_requirements": list(self.evidence_requirements),
        }


def remediation_fingerprint(
    *,
    plan_id: str,
    version: int,
    server_id: int | None,
    actions: list[dict[str, Any]],
    evidence_ids: list[str],
) -> str:
    """
    يبني بصمة ثابتة لخطة مرتبطة بإصدارها وسيرفرها وأدلتها وأفعالها.

    تستخدم البصمة لمنع تطبيق موافقة أو نتيجة sandbox على خطة تغيرت منذ إصدارها.
    """
    payload = {
        "plan_id": plan_id,
        "version": version,
        "server_id": server_id,
        "actions": actions,
        "evidence_ids": sorted(str(item) for item in evidence_ids),
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(slots=True, frozen=True)
class CreateRemediationPlanDTO:
    """
    البيانات اللازمة لإنشاء خطة معالجة مرتبطة بتحقيق وتشخيص وأدلة.

    لا تقبل الخطة أن تكون بلا أفعال أو ادعاءات تشخيص أو أدلة، لأن التغيير يجب
    أن يبدأ من سبب موثق لا من اقتراح معزول.
    """
    plan_id: str
    investigation_id: str
    title: str
    problem_summary: str
    proposed_actions: list[dict[str, Any]]
    diagnosis_claim_ids: list[str]
    evidence_ids: list[str]
    risk_level: str = RemediationRisk.MEDIUM.value
    rollback_plan: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    server_id: int | None = None
    plan_version: int = 1
    plan_fingerprint: str | None = None

    def __post_init__(self) -> None:
        """يتحقق من هوية الخطة وروابطها وأفعالها وخطرها وإصدارها."""
        for name in ("plan_id", "investigation_id", "title", "problem_summary"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty.")
        if not self.proposed_actions:
            raise ValueError("proposed_actions must not be empty.")
        if not self.diagnosis_claim_ids:
            raise ValueError("diagnosis_claim_ids must not be empty.")
        if not self.evidence_ids:
            raise ValueError("evidence_ids must not be empty.")
        if self.risk_level not in {item.value for item in RemediationRisk}:
            raise ValueError("risk_level is invalid.")
        if self.plan_version < 1:
            raise ValueError("plan_version must be >= 1.")


@dataclass(slots=True, frozen=True)
class CreateSandboxResultDTO:
    """
    نتيجة اختبار خطة في البيئة المعزولة مع أدلة الحالة قبل وبعد الاختبار.
    """
    result_id: str
    plan_id: str
    status: str
    before_evidence_ids: list[str]
    after_evidence_ids: list[str]
    logs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """يتحقق من هوية نتيجة الاختبار والخطة ومن أن حالتها passed أو failed."""
        if not self.result_id.strip():
            raise ValueError("result_id must not be empty.")
        if not self.plan_id.strip():
            raise ValueError("plan_id must not be empty.")
        if self.status not in {"passed", "failed"}:
            raise ValueError("sandbox status is invalid.")


@dataclass(slots=True, frozen=True)
class ApprovalRequest:
    """
    طلب موافقة صريح على خطة وبصمة محددتين قبل التغيير الفعلي.
    """
    approval_id: str
    plan_id: str
    plan_fingerprint: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver: str | None = None
    comment: str | None = None
    scope: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PolicyResult:
    """
    نتيجة تقييم السياسة مع قرارها والأسباب التي يمكن مراجعتها.
    """
    decision: PolicyDecision
    reasons: tuple[str, ...]

    @property
    def allowed(self) -> bool:
        """يحدد هل القرار يسمح بالمتابعة دون اعتبار وجود موافقة إضافية."""
        return self.decision == PolicyDecision.ALLOW
