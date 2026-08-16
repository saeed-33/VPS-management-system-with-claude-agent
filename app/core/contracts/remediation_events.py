"""
عقود وDTOs مشتركة لنقل البيانات بين الطبقات.

الموقع في المعمارية: Core application contracts.
يُستدعى بواسطة: capabilities وinterfaces وadapters.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا تنفذ I/O أو workflow.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RemediationEventType(StrEnum):
    """
    يمثل RemediationEventType مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على StrEnum وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
    يمثل RemediationEvent مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    event_type: RemediationEventType
    plan_id: str
    actor: str | None = None
    server_id: int | None = None
    runtime_session_id: str | None = None
    agent_job_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
