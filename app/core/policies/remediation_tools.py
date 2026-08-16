"""
قائمة أفعال التغيير المسموحة وأهداف خدماتها.

لا تسمح هذه الوحدة إلا بأفعال مسماة مثل بدء خدمة أو إيقافها، وتتحقق من اسم
الخدمة والمعاملات قبل توليد أمر systemctl ثابت.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.core.contracts.remediation import RemediationAction, RemediationRisk


SERVICE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@-]{0,127}$")


class RemediationToolValidationError(ValueError):
    """
    خطأ يوضح أن فعل تغيير أو هدفه لا يطابق قائمة الأفعال المسموحة.
    """
    pass


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


def build_default_write_tool_registry() -> NamedWriteToolRegistry:
    """
    يبني القائمة القياسية لأفعال الخدمات المسموحة ومستويات خطرها وإمكان التراجع.
    """
    return NamedWriteToolRegistry(
        (
            # الفعل الآلي الوحيد هنا أداة مسماة منخفضة الخطر ومذكورة صراحة في
            # القائمة المسموحة.
            NamedWriteTool("start_service", RemediationRisk.LOW.value, 30.0, "stop_service", "active"),
            NamedWriteTool("stop_service", RemediationRisk.HIGH.value, 30.0, "start_service", "inactive"),
            # تكرار إعادة التشغيل أو التحميل لا يعيد الحالة السابقة؛ لذلك لا
            # نعد بدعم التراجع حتى تتوفر استعادة حقيقية للعملية والإعدادات.
            NamedWriteTool("restart_service", RemediationRisk.HIGH.value, 45.0, None, "active"),
            NamedWriteTool("reload_service", RemediationRisk.MEDIUM.value, 30.0, None, "active"),
        )
    )


def action_from_tool_arguments(arguments: dict[str, Any]) -> RemediationAction:
    """
    يحول معاملات طلب أداة المعالجة إلى فعل مسمى يخضع لبقية التحققات.
    """
    action_type = arguments.get("action_type") or arguments.get("tool")
    if not isinstance(action_type, str) or not action_type.strip():
        raise RemediationToolValidationError("action_type is required.")
    target = arguments.get("target") or arguments.get("service")
    if not isinstance(target, str) or not target.strip():
        raise RemediationToolValidationError("target is required.")
    return RemediationAction(
        action_type=action_type,
        target=target,
        parameters=dict(arguments.get("parameters") or {}),
        reason=str(arguments.get("reason") or ""),
        expected_effect=str(arguments.get("expected_effect") or ""),
        action_id=str(arguments.get("action_id") or action_type),
    )
