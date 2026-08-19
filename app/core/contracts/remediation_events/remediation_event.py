"""Contract class extracted from remediation_events.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

from .remediation_event_type import RemediationEventType

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
