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

from .job_serialization import _JobSerializationMixin
from .serialization_helpers import _ObservabilitySerializationHelpersMixin
from .trace_queries import _TraceQueriesMixin


class ClaudeAgentObservabilityService(_TraceQueriesMixin, _JobSerializationMixin, _ObservabilitySerializationHelpersMixin):
    """
    خدمة تلخص آثار مهام Claude لتوضيح ما شغلته الجلسة وما انتهت إليه.
    """


    REQUIRED_OPERATIONAL_TOOLS = (
        "mcp__vps__run_monitoring",
        "mcp__vps__analyze_report",
    )

    def __init__(
        self,
        repository: AgentJobRepository,
    ) -> None:
        """
        يجهز مصادر قراءة المهام والتقارير اللازمة لبناء أثر تشغيل قابل للمراجعة.
        """
        self._repository = repository
