"""
Policy أو registry حتمي يقرر السماح أو الرفض أو التصنيف قبل التنفيذ.

الموقع في المعمارية: Core policy.
يُستدعى بواسطة: capabilities وMCP handlers.
يعتمد مباشرة على: app.core.contracts.sandbox_validation، app.core.policies.remediation_tools.
الحد المعماري: لا تنفذ SSH أو LLM أو persistence.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from app.core.contracts.sandbox_validation import SandboxTarget
from app.core.policies.remediation_tools import SERVICE_NAME_RE


SAFE_MARKERS = ("safe-remediation-test", "non-production")


def validate_sandbox_target(*, server, target: SandboxTarget) -> None:
    """
    يقيّم أو يتحقق من شرط حتمي قبل السماح بالخطوة التالية ضمن طبقة Core policy.

    تُستدعى عندما يصل workflow إلى validate_sandbox_target؛ المدخلات المهمة: server، target.
    تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    if server is None or server.id != target.server_id or server.name != target.server_name:
        raise ValueError("Sandbox target identity does not match the registered server.")
    if not SERVICE_NAME_RE.fullmatch(target.service):
        raise ValueError("Sandbox service is not a valid registered service identifier.")
    designation = (server.description or "").casefold()
    if any(marker not in designation for marker in SAFE_MARKERS):
        raise ValueError("Sandbox target is not explicitly designated safe and non-production.")
    if "production" in designation and "non-production" not in designation:
        raise ValueError("Production targets cannot be used for sandbox validation.")
