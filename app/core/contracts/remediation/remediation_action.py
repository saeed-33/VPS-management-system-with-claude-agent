"""Contract class extracted from remediation.py during the structure refactor."""

from __future__ import annotations

import hashlib

import json

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

from .remediation_risk import RemediationRisk

@dataclass(slots=True, frozen=True)
class RemediationAction:
    """
    فعل واحد داخل خطة المعالجة مع هدفه وخطره وشروط التحقق والتراجع.

    يصف العقد ما سيحدث، لكنه لا يمنح الإذن بتنفيذه ولا يقبل نص shell حرًا.
    """

    action_type: str
    target: str
    parameters: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    expected_effect: str = ""
    risk_level: str = RemediationRisk.MEDIUM.value
    requires_approval: bool = True
    rollback_supported: bool = False
    verification_strategy: str = ""
    evidence_requirements: tuple[str, ...] = ()
    action_id: str | None = None

    def __post_init__(self) -> None:
        """يتحقق من وجود نوع وهدف ومن أن مستوى الخطر معروف للنظام."""
        if not self.action_type.strip():
            raise ValueError("action_type must not be empty.")
        if not self.target.strip():
            raise ValueError("target must not be empty.")
        if self.risk_level not in {item.value for item in RemediationRisk}:
            raise ValueError("risk_level is invalid.")

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RemediationAction":
        """
        ينشئ فعل معالجة من تمثيل قادم من خطة أو سجل قديم.

        يوحد أسماء الحقول القديمة والجديدة ويحول متطلبات الأدلة إلى مجموعة
        ثابتة قبل تطبيق تحقق العقد.
        """
        if not isinstance(value, dict):
            raise ValueError("remediation actions must be objects.")
        action_type = str(
            value.get("action_type")
            or value.get("tool")
            or value.get("type")
            or "legacy"
        )
        target = str(value.get("target") or value.get("service") or "legacy")
        evidence = value.get("evidence_requirements", ())
        if not isinstance(evidence, (list, tuple)):
            raise ValueError("evidence_requirements must be a list.")
        return cls(
            action_type=action_type,
            target=target,
            parameters=dict(value.get("parameters") or {}),
            reason=str(value.get("reason") or value.get("description") or ""),
            expected_effect=str(value.get("expected_effect") or ""),
            risk_level=str(value.get("risk_level") or RemediationRisk.MEDIUM.value),
            requires_approval=bool(value.get("requires_approval", True)),
            rollback_supported=bool(value.get("rollback_supported", False)),
            verification_strategy=str(value.get("verification_strategy") or ""),
            evidence_requirements=tuple(str(item) for item in evidence),
            action_id=(str(value["id"]) if value.get("id") is not None else None),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        يحول فعل المعالجة إلى بيانات قابلة للحفظ أو الإرسال إلى واجهة الإدارة.
        """
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "target": self.target,
            "parameters": dict(self.parameters),
            "reason": self.reason,
            "expected_effect": self.expected_effect,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
            "rollback_supported": self.rollback_supported,
            "verification_strategy": self.verification_strategy,
            "evidence_requirements": list(self.evidence_requirements),
        }
