"""
Policy أو registry حتمي يقرر السماح أو الرفض أو التصنيف قبل التنفيذ.

الموقع في المعمارية: Core policy.
يُستدعى بواسطة: capabilities وMCP handlers.
يعتمد مباشرة على: app.core.contracts.remediation.
الحد المعماري: لا تنفذ SSH أو LLM أو persistence.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.core.contracts.remediation import (
    ApprovalStatus,
    PolicyDecision,
    PolicyResult,
    RemediationPlanStatus,
)


@dataclass(frozen=True, slots=True)
class RemediationPolicyEngine:
    """
    يمثل RemediationPolicyEngine مسؤولية محددة داخل طبقة Core policy.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وMCP handlers
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        يقيّم أو يتحقق من شرط حتمي قبل السماح بالخطوة التالية ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى evaluate_execution؛ المدخلات المهمة: plan، approval، requested_server_id، now.
        تعيد PolicyResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يقيّم أو يتحقق من شرط حتمي قبل السماح بالخطوة التالية ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى evaluate_action؛ المدخلات المهمة: registered، rollback_supported، verification_available.
        تعيد PolicyResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
