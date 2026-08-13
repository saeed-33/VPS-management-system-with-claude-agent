from __future__ import annotations

from app.core.contracts.remediation import RemediationAction, RemediationRisk
from app.core.policies.remediation_tools import NamedWriteToolRegistry


class RemediationRiskClassifier:
    """Deterministic risk rules; model output is never used for risk."""

    def __init__(self, registry: NamedWriteToolRegistry) -> None:
        self._registry = registry

    def classify(self, action: RemediationAction, *, server_metadata: dict | None = None) -> RemediationRisk:
        tool = self._registry.get(action.action_type)
        if tool is None:
            return RemediationRisk.CRITICAL
        tags = {str(item).lower() for item in (server_metadata or {}).get("tags", [])}
        if "production" in tags or "critical" in tags:
            if action.action_type in {"stop_service", "restart_service"}:
                return RemediationRisk.CRITICAL
        return RemediationRisk(tool.risk_level)

    def classify_actions(self, actions: list[RemediationAction], *, server_metadata: dict | None = None) -> RemediationRisk:
        levels = [self.classify(action, server_metadata=server_metadata) for action in actions]
        order = {risk: index for index, risk in enumerate(RemediationRisk)}
        return max(levels, key=lambda risk: order[risk]) if levels else RemediationRisk.CRITICAL
