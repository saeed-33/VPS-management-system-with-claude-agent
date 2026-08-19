"""Class extracted from diagnostic_policy during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any, Protocol

from app.core.contracts.investigation.investigation_budget import InvestigationBudget

from app.core.policies.diagnostic_tools.diagnostic_tool_call import DiagnosticToolCall
from app.core.policies.diagnostic_tools.diagnostic_tool_registry import DiagnosticToolRegistry
from app.core.policies.diagnostic_tools.diagnostic_tool_risk import DiagnosticToolRisk

class DiagnosticPolicyReason(StrEnum):
    """
    الأسباب التي تشرح رفض طلب تشخيص أو السماح به.
    """
    ALLOWED = "allowed"
    UNKNOWN_TOOL = "unknown_tool"
    TOOL_NOT_ALLOWED = "tool_not_allowed"
    UNSUPPORTED_RISK = "unsupported_risk"
    INVALID_ARGUMENTS = "invalid_arguments"
    SPECIALIST_ROUND_LIMIT = "specialist_round_limit"
    INVESTIGATION_ROUND_LIMIT = "investigation_round_limit"
    SPECIALIST_ACTION_LIMIT = "specialist_action_limit"
    INVESTIGATION_ACTION_LIMIT = "investigation_action_limit"
