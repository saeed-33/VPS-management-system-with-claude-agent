"""
سياسة السماح بطلبات أدوات التحقيق.

تتحقق من وجود الأداة وخطرها ومنحها للمتخصص وصحة معاملاتها وحدود الجولات
والأفعال، ولا تعرض الأمر التنفيذي إلا إذا اجتازت كل الشروط.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol

from app.core.contracts.investigation import InvestigationBudget
from app.core.policies.diagnostic_tools import (
    DiagnosticToolCall,
    DiagnosticToolRegistry,
    DiagnosticToolRisk,
)


class SpecialistPolicyDefinition(Protocol):
    """
    عقد يزود سياسة التشخيص بحدود المتخصص وأدواته المسموحة.
    """
    slug: str
    max_rounds: int
    max_actions: int
    allowed_tool_ids: tuple[str, ...]


class DiagnosticPolicyDecision(StrEnum):
    """
    القرار النهائي بشأن السماح بطلب أداة تشخيص أو منعه.
    """
    ALLOW = "allow"
    DENY = "deny"


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
