"""Contract class extracted from sandbox_validation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

from .sandbox_target import SandboxTarget

from .sandbox_validation_status import SandboxValidationStatus

@dataclass(frozen=True, slots=True)
class SandboxValidationResult:
    """
    سجل كامل لاختبار خطة معالجة في sandbox.

    يربط النتيجة بالخطة وبصمتها والهدف والأدلة قبل وبعد الاختبار والحالة التي
    كان يجب الوصول إليها، حتى لا تستخدم موافقة قديمة لخطة مختلفة.
    """
    validation_id: str
    plan_id: str
    plan_fingerprint: str
    target: SandboxTarget
    action_type: str
    action_parameters: dict[str, Any]
    expected_state: str
    observed_state: str | None
    before_evidence_ids: tuple[str, ...]
    after_evidence_ids: tuple[str, ...]
    verification_status: str
    status: SandboxValidationStatus
    started_at: datetime | None = None
    finished_at: datetime | None = None
    failure_reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
