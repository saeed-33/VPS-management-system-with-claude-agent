"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

from .autonomous_history_snapshot import AutonomousHistorySnapshot

from .autonomous_remediation_policy import AutonomousRemediationPolicy

@dataclass(slots=True, frozen=True)
class AutonomousEvaluationContext:
    """
    كل المعطيات التي تحتاجها سياسة المعالجة الذاتية لاتخاذ قرار آمن.

    يجمع السياق التشخيص والخطة ونتيجة sandbox والتاريخ والحدود الزمنية وحالة
    التنفيذ، حتى يكون القرار قابلًا لإعادة الفحص قبل الأثر الفعلي.
    """
    global_enabled: bool
    now: datetime
    policy: AutonomousRemediationPolicy | None
    plan_id: str
    plan_fingerprint: str
    issue_fingerprint: str
    server_id: int | None
    action_type: str
    target: str
    risk: str
    confidence: float
    diagnosis_evidence_valid: bool
    plan_evidence_valid: bool
    sandbox: Any | None
    history: AutonomousHistorySnapshot
    last_execution_at: datetime | None = None
    hourly_execution_count: int = 0
    daily_execution_count: int = 0
    consecutive_failures: int = 0
    execution_completed: bool = False
    execution_in_progress: bool = False
    plan_ready: bool = True
    ambiguous_policy_match: bool = False
    sandbox_evidence_valid: bool = False
    error_classification: str | None = None
