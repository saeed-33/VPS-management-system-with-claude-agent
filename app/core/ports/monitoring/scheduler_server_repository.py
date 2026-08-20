"""مكوّن جدولة مراقبة السيرفرات."""
from __future__ import annotations

from typing import Protocol

from .schedulable_server_record import SchedulableServerRecord

class SchedulerServerRepositoryProtocol(Protocol):
    """
    عقد يعيد السيرفرات المفعلة التي قد تستحق فحصًا جديدًا.
    """
    def list_enabled_servers(
        self,
    ) -> list[SchedulableServerRecord]:
        """
        يعرض بيانات جدولة المراقبة التي تحتاجها واجهة الإدارة أو الجدولة.
        """
        ...
