"""
جزء من Remediation من التشخيص والاقتراح حتى sandbox/authorization والتنفيذ.

الموقع في المعمارية: Application capability / remediation.
يُستدعى بواسطة: Admin API أو MCP.
يعتمد مباشرة على: app.core.contracts.autonomous_remediation.
الحد المعماري: لا يسمح write operation بمجرد اقتراح LLM.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from app.core.contracts.autonomous_remediation import AutonomousPolicyCandidate


class AutonomousCandidateService:
    """Read-only advisory discovery; it never creates or enables policies."""

    def __init__(self, *, repository) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: repository.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._repository = repository

    def list_candidates(self) -> list[AutonomousPolicyCandidate]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى list_candidates؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[AutonomousPolicyCandidate] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        result = []
        for (fingerprint, action_type, target), data in self._repository.candidate_keys().items():
            executions = data["executions"]
            successes = [item for item in executions if item.status == "succeeded"]
            failures = [item for item in executions if item.status != "succeeded"]
            verified_successes = len(data.get("verified_ids", set()) & {item.execution_id for item in successes})
            rollback_failures = len(data.get("rollback_failure_ids", set()))
            result.append(AutonomousPolicyCandidate(
                issue_fingerprint=fingerprint, action_type=action_type, target=target,
                execution_count=len(executions), verified_success_count=verified_successes, failure_count=len(failures),
                rollback_failure_count=rollback_failures,
                success_rate=len(successes) / len(executions) if executions else 0.0,
                reason_codes=("eligible_for_policy_review",) if verified_successes >= 3 and not failures and not rollback_failures else ("insufficient_verified_history",),
            ))
        return result
