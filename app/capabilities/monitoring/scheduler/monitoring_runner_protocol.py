"""مكوّن جدولة مراقبة السيرفرات."""
from __future__ import annotations

from typing import Protocol

class MonitoringRunnerProtocol(Protocol):
    """
    عقد لعامل يبدأ دورة مراقبة لسيرفر واحد.
    """
    async def run(
        self,
        server_id: int,
    ):
        """
        ينفذ عملية مرتبطة بـجدولة المراقبة ويساعد على نقل حالتها إلى المرحلة التالية.
        """
        ...
