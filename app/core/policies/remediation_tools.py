from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.core.contracts.remediation import RemediationAction, RemediationRisk


SERVICE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@-]{0,127}$")


class RemediationToolValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class NamedWriteTool:
    name: str
    risk_level: str
    timeout_seconds: float
    rollback_action: str | None
    expected_effect: str

    def validate(self, action: RemediationAction) -> None:
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
        self.validate(action)
        # The target has already passed a strict allow-list. No caller can
        # provide a command, shell fragment, or executable path.
        return f"systemctl {self.name.removesuffix('_service')} {action.target}"


class NamedWriteToolRegistry:
    def __init__(self, tools: tuple[NamedWriteTool, ...]) -> None:
        self._tools = {tool.name: tool for tool in tools}

    def get(self, name: str) -> NamedWriteTool | None:
        return self._tools.get(name)

    def require(self, name: str) -> NamedWriteTool:
        tool = self.get(name)
        if tool is None:
            raise RemediationToolValidationError(f"Unknown remediation write tool: {name}")
        return tool

    def resolve(self, action: RemediationAction) -> NamedWriteTool:
        tool = self.require(action.action_type)
        tool.validate(action)
        return tool

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))


def build_default_write_tool_registry() -> NamedWriteToolRegistry:
    return NamedWriteToolRegistry(
        (
            NamedWriteTool("start_service", RemediationRisk.MEDIUM.value, 30.0, "stop_service", "active"),
            NamedWriteTool("stop_service", RemediationRisk.HIGH.value, 30.0, "start_service", "inactive"),
            # A second restart/reload is the bounded compensating operation;
            # no arbitrary previous command is ever reconstructed.
            NamedWriteTool("restart_service", RemediationRisk.HIGH.value, 45.0, "restart_service", "active"),
            NamedWriteTool("reload_service", RemediationRisk.MEDIUM.value, 30.0, "reload_service", "active"),
        )
    )


def action_from_tool_arguments(arguments: dict[str, Any]) -> RemediationAction:
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
