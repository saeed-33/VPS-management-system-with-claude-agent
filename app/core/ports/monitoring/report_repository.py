"""مكوّن دورة مراقبة السيرفر."""
from __future__ import annotations

from typing import Any, Protocol

from app.core.contracts.reports.monitoring_report_data import MonitoringReportData

class ReportRepositoryPort(Protocol):
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

    def list_reports(
        self,
        *,
        server_id: int | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[tuple[Any, Any]]: ...

    def count_reports(
        self,
        *,
        server_id: int | None = None,
        status: str | None = None,
    ) -> int: ...

    def get_with_server(self, report_id: int) -> tuple[Any, Any] | None: ...
