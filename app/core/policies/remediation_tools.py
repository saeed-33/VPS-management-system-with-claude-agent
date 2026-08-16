"""
Policy أو registry حتمي يقرر السماح أو الرفض أو التصنيف قبل التنفيذ.

الموقع في المعمارية: Core policy.
يُستدعى بواسطة: capabilities وMCP handlers.
يعتمد مباشرة على: app.core.contracts.remediation.
الحد المعماري: لا تنفذ SSH أو LLM أو persistence.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.core.contracts.remediation import RemediationAction, RemediationRisk


SERVICE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@-]{0,127}$")


class RemediationToolValidationError(ValueError):
    """
    يمثل RemediationToolValidationError مسؤولية محددة داخل طبقة Core policy.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وMCP handlers
    ويعتمد على ValueError وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    pass


@dataclass(frozen=True, slots=True)
class NamedWriteTool:
    """
    يمثل NamedWriteTool مسؤولية محددة داخل طبقة Core policy.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وMCP handlers
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    name: str
    risk_level: str
    timeout_seconds: float
    rollback_action: str | None
    expected_effect: str

    def validate(self, action: RemediationAction) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى validate؛ المدخلات المهمة: action.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى command_for؛ المدخلات المهمة: action.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self.validate(action)
        # The target has already passed a strict allow-list. No caller can
        # provide a command, shell fragment, or executable path.
        return f"systemctl {self.name.removesuffix('_service')} {action.target}"


class NamedWriteToolRegistry:
    """
    يمثل NamedWriteToolRegistry مسؤولية محددة داخل طبقة Core policy.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وMCP handlers
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, tools: tuple[NamedWriteTool, ...]) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: tools.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._tools = {tool.name: tool for tool in tools}

    def get(self, name: str) -> NamedWriteTool | None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى get؛ المدخلات المهمة: name.
        تعيد NamedWriteTool | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._tools.get(name)

    def require(self, name: str) -> NamedWriteTool:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى require؛ المدخلات المهمة: name.
        تعيد NamedWriteTool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        tool = self.get(name)
        if tool is None:
            raise RemediationToolValidationError(f"Unknown remediation write tool: {name}")
        return tool

    def resolve(self, action: RemediationAction) -> NamedWriteTool:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى resolve؛ المدخلات المهمة: action.
        تعيد NamedWriteTool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        tool = self.require(action.action_type)
        tool.validate(action)
        return tool

    def names(self) -> tuple[str, ...]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى names؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد tuple[str, ...] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return tuple(sorted(self._tools))


def build_default_write_tool_registry() -> NamedWriteToolRegistry:
    """
    يبني DTO أو dependency graph من المدخلات ضمن طبقة Core policy.

    تُستدعى عندما يصل workflow إلى build_default_write_tool_registry؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد NamedWriteToolRegistry أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return NamedWriteToolRegistry(
        (
            # Phase 7 V1's only autonomous action is this explicitly
            # allowlisted, low-risk named tool.
            NamedWriteTool("start_service", RemediationRisk.LOW.value, 30.0, "stop_service", "active"),
            NamedWriteTool("stop_service", RemediationRisk.HIGH.value, 30.0, "start_service", "inactive"),
            # Repeating restart/reload does not restore a prior known state.
            # They remain registered actions, but cannot claim rollback support
            # until a real previous-process/config restoration exists.
            NamedWriteTool("restart_service", RemediationRisk.HIGH.value, 45.0, None, "active"),
            NamedWriteTool("reload_service", RemediationRisk.MEDIUM.value, 30.0, None, "active"),
        )
    )


def action_from_tool_arguments(arguments: dict[str, Any]) -> RemediationAction:
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core policy.

    تُستدعى عندما يصل workflow إلى action_from_tool_arguments؛ المدخلات المهمة: arguments.
    تعيد RemediationAction أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
