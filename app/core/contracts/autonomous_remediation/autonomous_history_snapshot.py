"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

@dataclass(slots=True, frozen=True)
class AutonomousHistorySnapshot:
    """
    ملخص تاريخي لنجاح وفشل معالجة نفس المشكلة والفعل والهدف.

    تستخدمه السياسة لمعرفة هل يملك العلاج سجل نجاح كافيًا وهل تجاوز معدل الفشل
    أو فشل التراجع الحد الذي يوقف التنفيذ الذاتي.
    """
    issue_fingerprint: str
    action_type: str
    target: str
    supervised_execution_count: int = 0
    successful_execution_count: int = 0
    failed_execution_count: int = 0
    verified_success_count: int = 0
    verification_failure_count: int = 0
    rollback_required_count: int = 0
    rollback_success_count: int = 0
    rollback_failure_count: int = 0
    autonomous_execution_count: int = 0
    autonomous_success_count: int = 0
    autonomous_failure_count: int = 0
    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None

    @property
    def success_rate(self) -> float:
        """يحسب نسبة النجاحات المتحققة من إجمالي التنفيذات المراقبة."""
        return self.verified_success_count / self.supervised_execution_count if self.supervised_execution_count else 0.0

    @property
    def failure_rate(self) -> float:
        """يحسب نسبة التنفيذات الفاشلة التي يجب أن تؤثر على قرار السياسة."""
        return self.failed_execution_count / self.supervised_execution_count if self.supervised_execution_count else 0.0

    @property
    def rollback_failure_rate(self) -> float:
        """يحسب نسبة عمليات التراجع الفاشلة بين الحالات التي احتاجت تراجعًا."""
        return self.rollback_failure_count / self.rollback_required_count if self.rollback_required_count else 0.0
