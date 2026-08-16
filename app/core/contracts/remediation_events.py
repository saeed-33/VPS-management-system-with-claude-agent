"""عقد سجل الأحداث الذي يتتبع خطة المعالجة من الاقتراح حتى التراجع."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RemediationEventType(StrEnum):
    """
    أنواع انتقال خطة المعالجة ونتيجة تنفيذها والتحقق منها.
    """
    PROPOSED = "proposed"
    SANDBOX_PASSED = "sandbox_passed"
    SANDBOX_FAILED = "sandbox_failed"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_REJECTED = "approval_rejected"
    APPROVAL_EXPIRED = "approval_expired"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_FAILED = "execution_failed"
    VERIFICATION_FAILED = "verification_failed"
    EXECUTION_SUCCEEDED = "execution_succeeded"
    ROLLBACK_SUCCEEDED = "rollback_succeeded"
    ROLLBACK_FAILED = "rollback_failed"


@dataclass(frozen=True, slots=True)
class RemediationEvent:
    """
    حدث تدقيق يربط انتقال الخطة بالفاعل والسيرفر والجلسة والبيانات المساندة.

    يسمح السجل بإعادة بناء ما حدث قبل التغيير وأثناءه وبعده، بما في ذلك نتيجة
    التحقق أو التراجع.
    """
    event_type: RemediationEventType
    plan_id: str
    actor: str | None = None
    server_id: int | None = None
    runtime_session_id: str | None = None
    agent_job_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
