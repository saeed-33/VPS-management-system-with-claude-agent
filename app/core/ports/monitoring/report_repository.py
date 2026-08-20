"""مكوّن دورة مراقبة السيرفر."""
from __future__ import annotations

from typing import Protocol

class ReportRepositoryProtocol(Protocol):
    """
    عقد يحفظ تقرير القياسات الناتج من دورة المراقبة.
    """
    def create(
        self,
        report: MonitoringReportData,
    ) -> int:
        """
        ينشئ أو يربط سجلًا داخل دورة مراقبة السيرفر بعد تحقق القيم اللازمة.
        """
        ...
