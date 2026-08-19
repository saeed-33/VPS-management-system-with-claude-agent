"""Contract class extracted from remediation.py during the structure refactor."""

from __future__ import annotations

import hashlib

import json

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

from .remediation_risk import RemediationRisk

@dataclass(slots=True, frozen=True)
class CreateRemediationPlanDTO:
    """
    البيانات اللازمة لإنشاء خطة معالجة مرتبطة بتحقيق وتشخيص وأدلة.

    لا تقبل الخطة أن تكون بلا أفعال أو ادعاءات تشخيص أو أدلة، لأن التغيير يجب
    أن يبدأ من سبب موثق لا من اقتراح معزول.
    """
    plan_id: str
    investigation_id: str
    title: str
    problem_summary: str
    proposed_actions: list[dict[str, Any]]
    diagnosis_claim_ids: list[str]
    evidence_ids: list[str]
    risk_level: str = RemediationRisk.MEDIUM.value
    rollback_plan: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    server_id: int | None = None
    plan_version: int = 1
    plan_fingerprint: str | None = None

    def __post_init__(self) -> None:
        """يتحقق من هوية الخطة وروابطها وأفعالها وخطرها وإصدارها."""
        for name in ("plan_id", "investigation_id", "title", "problem_summary"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty.")
        if not self.proposed_actions:
            raise ValueError("proposed_actions must not be empty.")
        if not self.diagnosis_claim_ids:
            raise ValueError("diagnosis_claim_ids must not be empty.")
        if not self.evidence_ids:
            raise ValueError("evidence_ids must not be empty.")
        if self.risk_level not in {item.value for item in RemediationRisk}:
            raise ValueError("risk_level is invalid.")
        if self.plan_version < 1:
            raise ValueError("plan_version must be >= 1.")
