"""Class extracted from diagnostic_policy during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any, Protocol

from app.core.contracts.investigation.investigation_budget import InvestigationBudget

from app.core.policies.diagnostic_tools.diagnostic_tool_call import DiagnosticToolCall
from app.core.policies.diagnostic_tools.diagnostic_tool_registry import DiagnosticToolRegistry
from app.core.policies.diagnostic_tools.diagnostic_tool_risk import DiagnosticToolRisk

from .diagnostic_policy_decision import DiagnosticPolicyDecision

from .diagnostic_policy_reason import DiagnosticPolicyReason

@dataclass(slots=True, frozen=True)
class DiagnosticPolicyResult:
    """
    نتيجة تقييم طلب التشخيص، ولا تكشف الأمر إلا عند السماح.
    """
    decision: DiagnosticPolicyDecision
    reasons: tuple[DiagnosticPolicyReason, ...]
    specialist_slug: str
    tool_id: str
    rendered_command: str | None = None
    timeout_seconds: float | None = None
    output_limit_chars: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def allowed(self) -> bool:
        """
        يحدد هل نتيجة السياسة تسمح بتنفيذ أداة التشخيص.
        """
        return self.decision == DiagnosticPolicyDecision.ALLOW

    def __post_init__(self) -> None:
        """
        يتحقق من أن عدادات طلب التشخيص ورقم جولته لا تحمل قيمًا غير صالحة.
        """
        if not self.specialist_slug.strip():
            raise ValueError("specialist_slug must not be empty.")
        if not self.tool_id.strip():
            raise ValueError("tool_id must not be empty.")
        if not self.reasons:
            raise ValueError("DiagnosticPolicyResult requires reasons.")

        if self.allowed:
            if self.reasons != (DiagnosticPolicyReason.ALLOWED,):
                raise ValueError(
                    "Allowed result must contain only the allowed reason."
                )
            if not self.rendered_command:
                raise ValueError(
                    "Allowed result requires rendered_command."
                )
            if self.timeout_seconds is None or self.timeout_seconds <= 0:
                raise ValueError(
                    "Allowed result requires positive timeout_seconds."
                )
            if self.output_limit_chars is None or self.output_limit_chars < 1:
                raise ValueError(
                    "Allowed result requires output_limit_chars."
                )
        else:
            if DiagnosticPolicyReason.ALLOWED in self.reasons:
                raise ValueError(
                    "Denied result cannot include allowed."
                )
            if self.rendered_command is not None:
                raise ValueError(
                    "Denied result must not expose rendered_command."
                )
