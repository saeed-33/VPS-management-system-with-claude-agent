"""مكوّن دورة مراقبة السيرفر."""
from __future__ import annotations

from typing import Protocol

class MonitoringCommandRecord(Protocol):
    """
    عقد يمثل فحصًا مفعّلًا مع نصه وترتيبه ومهلة تنفيذه.
    """
    id: int
    name: str
    command: str
    timeout_seconds: float
    execution_order: int
