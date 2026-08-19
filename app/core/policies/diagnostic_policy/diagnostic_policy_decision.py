"""Class extracted from diagnostic_policy during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any, Protocol

from app.core.contracts.investigation.investigation_budget import InvestigationBudget

from app.core.policies.diagnostic_tools.diagnostic_tool_call import DiagnosticToolCall
from app.core.policies.diagnostic_tools.diagnostic_tool_registry import DiagnosticToolRegistry
from app.core.policies.diagnostic_tools.diagnostic_tool_risk import DiagnosticToolRisk

class DiagnosticPolicyDecision(StrEnum):
    """
    القرار النهائي بشأن السماح بطلب أداة تشخيص أو منعه.
    """
    ALLOW = "allow"
    DENY = "deny"
