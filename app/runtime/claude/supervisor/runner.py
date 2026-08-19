"""عقد عامل المراقبة."""
from typing import Protocol

class MonitoringRunner(Protocol):
    """
    عقد لعامل يبدأ دورة مراقبة مرتبطة بسيرفر محدد.
    """
    async def run(self, server_id: int):
        """
        يبدأ دورة المراقبة للسيرفر المحدد ويعيد نتيجتها التشغيلية.
        """
        ...

