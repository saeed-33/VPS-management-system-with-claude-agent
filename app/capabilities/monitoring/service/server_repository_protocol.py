"""مكوّن دورة مراقبة السيرفر."""
from __future__ import annotations

from typing import Protocol

from datetime import datetime

class ServerRepositoryProtocol(Protocol):
    """
    عقد القراءة والتحديث الذي تحتاجه دورة المراقبة من مستودع السيرفر.
    """
    def get_by_id(
        self,
        server_id: int,
    ) -> ServerRecord | None:
        """
        يسترجع قيمة من دورة مراقبة السيرفر مرتبطة بالمعرف أو المفتاح المطلوب.
        """
        ...

    def update_monitoring_status(
        self,
        *,
        server_id: int,
        status: str,
        checked_at: datetime,
        success_at: datetime | None,
        error_message: str | None,
        report_id: int | None,
    ) -> None:
        """
        يغير حالة أو علاقة في دورة مراقبة السيرفر مع الحفاظ على اتساق السجلات المرتبطة.
        """
        ...
