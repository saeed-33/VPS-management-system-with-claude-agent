"""Class extracted from remediation_tools during the structure refactor."""

from __future__ import annotations

import re

from dataclasses import dataclass

from typing import Any

from app.core.contracts.remediation.remediation_action import RemediationAction
from app.core.contracts.remediation.remediation_risk import RemediationRisk

from .remediation_tool_validation_error import RemediationToolValidationError

from .constants import SERVICE_NAME_RE

@dataclass(frozen=True, slots=True)
class NamedWriteTool:
    """
    فعل تغيير مسمى يحدد خطر التنفيذ ووقته وإمكان التراجع وأثره المتوقع.
    """
    name: str
    risk_level: str
    timeout_seconds: float
    rollback_action: str | None
    expected_effect: str

    def validate(self, action: RemediationAction) -> None:
        """
        يتحقق من تطابق الفعل مع الأداة ومن سلامة اسم الخدمة ومعاملاتها.
        """
        if action.action_type != self.name:
            raise RemediationToolValidationError("Action type does not match the registered tool.")
        if not SERVICE_NAME_RE.fullmatch(action.target):
            raise RemediationToolValidationError(
                "Service target is invalid; only a named system service is accepted."
            )
        if action.parameters:
            unknown = set(action.parameters) - {"desired_state"}
            if unknown:
                raise RemediationToolValidationError(
                    "Unknown write-tool parameters: " + ", ".join(sorted(unknown))
                )

    def command_for(self, action: RemediationAction) -> str:
        """
        يولد أمر systemctl ثابتًا بعد اجتياز التحقق، ولا يقبل نص أوامر من الطلب.
        """
        self.validate(action)
        # اجتاز الهدف قائمة مسموحة ضيقة؛ لا يستطيع الطلب تمرير أمر أو جزء
        # من shell أو مسار تنفيذي من الخارج.
        return f"systemctl {self.name.removesuffix('_service')} {action.target}"
