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

from .diagnostic_policy_request import DiagnosticPolicyRequest

from .diagnostic_policy_result import DiagnosticPolicyResult

from .specialist_policy_definition import SpecialistPolicyDefinition

class DiagnosticPolicyEngine:
    """
    محرك يفرض الصلاحيات والمخاطر والميزانية قبل تشغيل أداة تشخيص.
    """
    def __init__(
        self,
        *,
        registry: DiagnosticToolRegistry,
        allowed_risks: tuple[DiagnosticToolRisk, ...] = (
            DiagnosticToolRisk.READ_ONLY,
        ),
    ) -> None:
        """
        يجهز سجل الأدوات ومجموعة مستويات الخطر التي يسمح بها التحقيق.
        """
        self._registry = registry
        self._allowed_risks = frozenset(allowed_risks)

        if not self._allowed_risks:
            raise ValueError(
                "Diagnostic policy must allow at least one risk class."
            )

    def evaluate(
        self,
        *,
        specialist: SpecialistPolicyDefinition,
        request: DiagnosticPolicyRequest,
    ) -> DiagnosticPolicyResult:
        """
        يفحص الأداة والمتخصص والميزانية والمعاملات، ثم يعيد أمرًا مضبوطًا فقط عند اجتياز كل البوابات.
        """
        tool_id = request.call.tool_id.strip().casefold()
        reasons: list[DiagnosticPolicyReason] = []

        if request.round_number > specialist.max_rounds:
            reasons.append(
                DiagnosticPolicyReason.SPECIALIST_ROUND_LIMIT
            )

        if (
            request.round_number
            > request.investigation_budget.max_rounds
        ):
            reasons.append(
                DiagnosticPolicyReason.INVESTIGATION_ROUND_LIMIT
            )

        if (
            request.specialist_actions_used
            >= specialist.max_actions
        ):
            reasons.append(
                DiagnosticPolicyReason.SPECIALIST_ACTION_LIMIT
            )

        if (
            request.investigation_actions_used
            >= request.investigation_budget.max_actions
        ):
            reasons.append(
                DiagnosticPolicyReason.INVESTIGATION_ACTION_LIMIT
            )

        definition = self._registry.get(tool_id)

        if definition is None:
            reasons.append(DiagnosticPolicyReason.UNKNOWN_TOOL)
            return self._deny(
                specialist=specialist,
                tool_id=tool_id,
                reasons=reasons,
                request=request,
            )

        if definition.risk not in self._allowed_risks:
            reasons.append(
                DiagnosticPolicyReason.UNSUPPORTED_RISK
            )

        allowed_ids = {
            value.strip().casefold()
            for value in specialist.allowed_tool_ids
            if value.strip()
        }

        if tool_id not in allowed_ids:
            reasons.append(
                DiagnosticPolicyReason.TOOL_NOT_ALLOWED
            )

        if reasons:
            return self._deny(
                specialist=specialist,
                tool_id=tool_id,
                reasons=reasons,
                request=request,
                definition=definition,
            )

        try:
            rendered_command = definition.render_command(
                request.call.arguments
            )
        except ValueError as exc:
            return self._deny(
                specialist=specialist,
                tool_id=tool_id,
                reasons=[
                    DiagnosticPolicyReason.INVALID_ARGUMENTS
                ],
                request=request,
                definition=definition,
                error=str(exc),
            )

        return DiagnosticPolicyResult(
            decision=DiagnosticPolicyDecision.ALLOW,
            reasons=(DiagnosticPolicyReason.ALLOWED,),
            specialist_slug=specialist.slug,
            tool_id=tool_id,
            rendered_command=rendered_command,
            timeout_seconds=definition.timeout_seconds,
            output_limit_chars=definition.output_limit_chars,
            metadata={
                "risk": definition.risk.value,
                "requires_sudo": definition.requires_sudo,
                "round_number": request.round_number,
                "specialist_actions_used": (
                    request.specialist_actions_used
                ),
                "specialist_max_actions": specialist.max_actions,
                "investigation_actions_used": (
                    request.investigation_actions_used
                ),
                "investigation_max_actions": (
                    request.investigation_budget.max_actions
                ),
            },
        )

    @staticmethod
    def _deny(
        *,
        specialist: SpecialistPolicyDefinition,
        tool_id: str,
        reasons: list[DiagnosticPolicyReason],
        request: DiagnosticPolicyRequest,
        definition=None,
        error: str | None = None,
    ) -> DiagnosticPolicyResult:
        """
        يبني نتيجة رفض تحفظ أسباب المنع والعدادات والخطر دون كشف أمر قابل للتنفيذ.
        """
        metadata: dict[str, Any] = {
            "round_number": request.round_number,
            "specialist_actions_used": (
                request.specialist_actions_used
            ),
            "specialist_max_actions": specialist.max_actions,
            "investigation_actions_used": (
                request.investigation_actions_used
            ),
            "investigation_max_actions": (
                request.investigation_budget.max_actions
            ),
        }

        if definition is not None:
            metadata["risk"] = definition.risk.value
            metadata["requires_sudo"] = definition.requires_sudo

        if error:
            metadata["validation_error"] = error

        return DiagnosticPolicyResult(
            decision=DiagnosticPolicyDecision.DENY,
            reasons=tuple(dict.fromkeys(reasons)),
            specialist_slug=specialist.slug,
            tool_id=tool_id,
            metadata=metadata,
        )
