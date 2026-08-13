from __future__ import annotations

from app.core.contracts.autonomous_remediation import AutonomousHistorySnapshot


class AutonomousHistoryService:
    def __init__(self, *, repository) -> None:
        self._repository = repository

    def snapshot(self, *, issue_fingerprint: str, action_type: str, target: str) -> AutonomousHistorySnapshot:
        return self._repository.history(issue_fingerprint=issue_fingerprint, action_type=action_type, target=target)

