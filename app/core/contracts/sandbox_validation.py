"""عقود اختبار خطة المعالجة في بيئة معزولة قبل لمس السيرفر الفعلي."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class SandboxValidationStatus(StrEnum):
    """
    حالات اختبار الخطة من الانتظار حتى النجاح أو الفشل أو انتهاء الصلاحية.
    """
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class SandboxTarget:
    """
    هوية السيرفر والخدمة التي ستختبر الخطة أثرها عليهما.
    """
    server_id: int
    server_name: str
    service: str
    designation: str

    def __post_init__(self) -> None:
        """يتحقق من أن هدف الاختبار يملك سيرفرًا وخدمة معروفين."""
        if self.server_id < 1 or not self.server_name.strip() or not self.service.strip():
            raise ValueError("Sandbox target identity is incomplete.")


@dataclass(frozen=True, slots=True)
class SandboxRuntimeCheck:
    """
    نتيجة فحص توفر بيئة الاختبار قبل تشغيل الخطة فيها.
    """
    available: bool
    runtime: str
    reason: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)


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
