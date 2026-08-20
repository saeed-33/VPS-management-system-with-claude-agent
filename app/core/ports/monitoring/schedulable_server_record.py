"""مكوّن جدولة مراقبة السيرفرات."""
from __future__ import annotations

from typing import Protocol

class SchedulableServerRecord(Protocol):
    """
    عقد يحمل بيانات السيرفر التي تحتاجها الجدولة لمعرفة موعد فحصه.
    """
    id: int
    interval_seconds: int
    monitor_enabled: bool
