"""
قراءة آثار مهام Claude وعرض نشاطها التشغيلي.

تجمع الخدمة حالة المهمة والجلسة والأدوات والمدة والاستخدام في بيانات تساعد على
معرفة ما حدث أثناء المراقبة دون الخلط بين أثر التشغيل وتشخيص السيرفر.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from app.infrastructure.database.repositories.agent_job_repository import (
    AgentJobRepository,
)


class _ObservabilitySerializationHelpersMixin:
    """ينظم مجموعة من عمليات المكون."""

    @staticmethod
    def _duration_ms(
        started_at: datetime | None,
        completed_at: datetime | None,
    ) -> float | None:
        """
        يحسب مدة المهمة بالميلي ثانية من أوقاتها المحفوظة أو يعيد قيمة فارغة عند غيابها.
        """
        if (
            started_at is None
            or completed_at is None
        ):
            return None

        return (
            completed_at - started_at
        ).total_seconds() * 1000.0

    @staticmethod
    def _number(
        value: Any,
    ) -> int | float | None:
        """
        يقرأ قيمة رقمية من بيانات الأثر مع منع القيم غير الصالحة من إفساد الملخص.
        """
        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            return value

        return None

    @staticmethod
    def _iso(
        value: datetime | None,
    ) -> str | None:
        """
        يحول وقت المهمة إلى نص زمني موحد للاستخدام في سجل الأثر.
        """
        if value is None:
            return None

        return value.isoformat()
