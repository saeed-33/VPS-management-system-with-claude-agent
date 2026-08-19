"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

from .autonomous_policy_status import AutonomousPolicyStatus

@dataclass(slots=True, frozen=True)
class AutonomousRemediationPolicy:
    """
    سياسة تحدد متى يمكن تنفيذ علاج معين تلقائيًا لسيرفر محدد.

    تجمع السياسة الخطر والثقة والأدلة والاختبار والتراجع وحدود المعدل والتاريخ،
    حتى لا يتحول تشخيص واحد إلى صلاحية عامة لتغيير السيرفرات.
    """
    policy_id: str
    name: str
    description: str
    status: AutonomousPolicyStatus
    version: int
    issue_fingerprint: str
    allowed_action_type: str
    allowed_target_pattern: str
    maximum_risk: str = "low"
    minimum_confidence: float = 0.0
    required_evidence: tuple[str, ...] = ("diagnosis", "plan", "sandbox_before", "sandbox_after", "verification")
    minimum_success_count: int = 0
    maximum_failure_rate: float = 0.0
    maximum_rollback_failure_rate: float = 0.0
    allowed_server_ids: tuple[int, ...] = ()
    allowed_server_tags: tuple[str, ...] = ()
    sandbox_required: bool = True
    sandbox_max_age_seconds: int = 3600
    rollback_required: bool = True
    cooldown_seconds: int = 0
    max_executions_per_hour: int = 1
    max_executions_per_day: int = 3
    max_consecutive_failures: int = 1
    auto_suspend_on_failure: bool = True
    created_by: str = "admin"
    updated_by: str = "admin"
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """يتحقق من هوية السياسة وإصدارتها وحدود الثقة والفشل والتكرار."""
        if not self.policy_id.strip() or not self.name.strip():
            raise ValueError("policy_id and name must not be empty.")
        if self.version < 1:
            raise ValueError("policy version must be >= 1.")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("minimum_confidence must be between 0 and 1.")
        if not 0 <= self.maximum_failure_rate <= 1:
            raise ValueError("maximum_failure_rate must be between 0 and 1.")
        if not 0 <= self.maximum_rollback_failure_rate <= 1:
            raise ValueError("maximum_rollback_failure_rate must be between 0 and 1.")
        for value in (self.sandbox_max_age_seconds, self.max_executions_per_hour, self.max_executions_per_day, self.max_consecutive_failures):
            if value < 1:
                raise ValueError("policy limits must be positive.")
