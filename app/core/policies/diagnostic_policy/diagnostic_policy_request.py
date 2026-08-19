"""Class extracted from diagnostic_policy during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any, Protocol

from app.core.contracts.investigation.investigation_budget import InvestigationBudget

from app.core.policies.diagnostic_tools.diagnostic_tool_call import DiagnosticToolCall
from app.core.policies.diagnostic_tools.diagnostic_tool_registry import DiagnosticToolRegistry
from app.core.policies.diagnostic_tools.diagnostic_tool_risk import DiagnosticToolRisk

@dataclass(slots=True, frozen=True)
class DiagnosticPolicyRequest:
    """
    بيانات طلب أداة تشخيص مع الجولة والعدادات والميزانية الحالية.
    """
    call: DiagnosticToolCall
    round_number: int
    specialist_actions_used: int
    investigation_actions_used: int
    investigation_budget: InvestigationBudget

    def __post_init__(self) -> None:
        """
        يتحقق من أن عدادات طلب التشخيص ورقم جولته لا تحمل قيمًا غير صالحة.
        """
        if self.round_number < 1:
            raise ValueError("round_number must be >= 1.")
        if self.specialist_actions_used < 0:
            raise ValueError("specialist_actions_used must be >= 0.")
        if self.investigation_actions_used < 0:
            raise ValueError("investigation_actions_used must be >= 0.")
