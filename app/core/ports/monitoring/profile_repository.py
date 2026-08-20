"""مكوّن دورة مراقبة السيرفر."""
from __future__ import annotations

from typing import Protocol

from .monitoring_command_record import MonitoringCommandRecord

class MonitoringProfileRepositoryProtocol(
    Protocol
):
    """
    عقد يجلب الفحوص المفعلة المرتبطة بسيرفر.
    """
    def list_enabled_commands_for_server(
        self,
        server_id: int,
    ) -> list[MonitoringCommandRecord]:
        """
        يعرض بيانات دورة مراقبة السيرفر التي تحتاجها واجهة الإدارة أو الجدولة.
        """
        ...
