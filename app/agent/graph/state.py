from typing import Any, TypedDict


class MonitoringGraphState(
    TypedDict,
    total=False,
):
    server_id: int

    report: Any
    report_id: int | None

    success: bool
    error_message: str | None