"""
سياسة الانتقال من خطة معالجة إلى تغيير فعلي على السيرفر.

تطلب الخطة موافقة صحيحة وبصمة مطابقة وأداة مسجلة وإمكان التحقق والتراجع قبل
السماح بالتنفيذ.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.core.contracts.remediation.approval_status import ApprovalStatus
from app.core.contracts.remediation.policy_decision import PolicyDecision
from app.core.contracts.remediation.policy_result import PolicyResult
from app.core.contracts.remediation.remediation_plan_status import RemediationPlanStatus


@dataclass(frozen=True, slots=True)
class RemediationPolicyEngine:
    """
    محرك يراجع جاهزية خطة المعالجة قبل تطبيقها على السيرفر.
    """
    automatic_remediation_allowed: bool = False

    def evaluate_execution(
        self,
        *,
        plan,
        approval,
        requested_server_id: int | None,
        now: datetime,
    ) -> PolicyResult:
        """
        يتحقق من ارتباط الطلب بالسيرفر والخطة والموافقة والبصمة وحالة الخطة قبل التنفيذ.
        """
        reasons: list[str] = []
        if requested_server_id is None or plan.server_id is None or requested_server_id != plan.server_id:
            reasons.append("wrong_or_missing_server")
        if approval is None:
            reasons.append("approval_missing")
        else:
            if approval.status != ApprovalStatus.APPROVED.value:
                reasons.append(f"approval_{approval.status}")
            if approval.plan_fingerprint != plan.plan_fingerprint:
                reasons.append("stale_plan_fingerprint")
            if approval.expires_at is not None:
                expires_at = approval.expires_at
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=now.tzinfo)
                if expires_at <= now:
                    reasons.append("approval_expired")
        if plan.status not in {RemediationPlanStatus.APPROVED.value, RemediationPlanStatus.SANDBOX_PASSED.value}:
            reasons.append("plan_not_ready")
        if self.automatic_remediation_allowed is False and (
            approval is None or approval.status != ApprovalStatus.APPROVED.value
        ):
            reasons.append("automatic_remediation_disabled_without_human_approval")
        if reasons:
            return PolicyResult(
                PolicyDecision.REQUIRE_APPROVAL
                if any(item.startswith("approval") or item == "approval_missing" for item in reasons)
                else PolicyDecision.DENY,
                tuple(reasons),
            )
        return PolicyResult(PolicyDecision.ALLOW, ())

    def evaluate_action(self, *, registered: bool, rollback_supported: bool, verification_available: bool) -> PolicyResult:
        """
        يتحقق من تسجيل فعل الكتابة وإمكان التراجع وتوفر التحقق قبل السماح بإدراجه في خطة قابلة للتنفيذ.
        """
        reasons: list[str] = []
        if not registered:
            reasons.append("unknown_write_tool")
        if not rollback_supported:
            reasons.append("rollback_not_supported")
        if not verification_available:
            reasons.append("verification_unavailable")
        if reasons:
            return PolicyResult(PolicyDecision.REQUIRE_ADDITIONAL_VALIDATION, tuple(reasons))
        return PolicyResult(PolicyDecision.ALLOW, ())
