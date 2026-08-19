"""Contract class extracted from remediation.py during the structure refactor."""

from __future__ import annotations

import hashlib

import json

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

from .approval_status import ApprovalStatus

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
