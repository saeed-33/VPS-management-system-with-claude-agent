"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

from .autonomous_authorization_status import AutonomousAuthorizationStatus

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
