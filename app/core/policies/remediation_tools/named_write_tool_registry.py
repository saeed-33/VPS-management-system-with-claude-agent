"""Class extracted from remediation_tools during the structure refactor."""

from __future__ import annotations

import re

from dataclasses import dataclass

from typing import Any

from app.core.contracts.remediation.remediation_action import RemediationAction
from app.core.contracts.remediation.remediation_risk import RemediationRisk

from .named_write_tool import NamedWriteTool

from .remediation_tool_validation_error import RemediationToolValidationError

class NamedWriteToolRegistry:
    """
    سجل الأفعال الكتابية المسموحة الذي يمنع تنفيذ فعل غير معروف.
    """
    def __init__(self, tools: tuple[NamedWriteTool, ...]) -> None:
        """
        يبني سجل الأفعال المسماة التي يمكن لخدمات المعالجة حلها.
        """
        self._tools = {tool.name: tool for tool in tools}

    def get(self, name: str) -> NamedWriteTool | None:
        """
        يبحث عن فعل تغيير مسجل دون اعتبار غيابه إذنًا بالتنفيذ.
        """
        return self._tools.get(name)

    def require(self, name: str) -> NamedWriteTool:
        """
        يسترجع فعلًا مسجلًا أو يرفض الطلب إذا كان نوع التغيير مجهولًا.
        """
        tool = self.get(name)
        if tool is None:
            raise RemediationToolValidationError(f"Unknown remediation write tool: {name}")
        return tool

    def resolve(self, action: RemediationAction) -> NamedWriteTool:
        """
        يحل فعل الخطة إلى تعريفه المسجل ويعيد التحقق من هدفه قبل التنفيذ.
        """
        tool = self.require(action.action_type)
        tool.validate(action)
        return tool

    def names(self) -> tuple[str, ...]:
        """
        يعيد أسماء أفعال التغيير المسجلة لعرضها أو مطابقتها مع السياسة.
        """
        return tuple(sorted(self._tools))
