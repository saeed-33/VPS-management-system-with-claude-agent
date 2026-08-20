"""
قراءة ملخص تاريخ المعالجة الآلية.

تجمع الخدمة قرارات التنفيذ والحجوزات والتفويضات وأحداث التدقيق في لقطة واحدة
للمراقبة والواجهات الإدارية.
"""
from __future__ import annotations

from app.core.contracts.autonomous_remediation.autonomous_history_snapshot import AutonomousHistorySnapshot
from app.core.ports.remediation.autonomous_remediation_repository import AutonomousRemediationRepositoryPort


class AutonomousHistoryService:
    """
    يبني لقطة تاريخية موحدة لعمليات المعالجة الآلية المرتبطة بالسيرفر أو التشخيص.
    """
    def __init__(self, *, repository: AutonomousRemediationRepositoryPort) -> None:
        """
        يربط مستودعات قرارات وحجوزات وتفويضات وأحداث المعالجة الآلية.
        """
        self._repository = repository

    def snapshot(self, *, issue_fingerprint: str, action_type: str, target: str) -> AutonomousHistorySnapshot:
        """
        يجمع أحدث القرارات والحجوزات والتفويضات والتدقيق في لقطة تاريخية.
        """
        return self._repository.history(issue_fingerprint=issue_fingerprint, action_type=action_type, target=target)
