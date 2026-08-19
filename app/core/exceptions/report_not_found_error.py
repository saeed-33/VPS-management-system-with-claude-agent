"""Class extracted from exceptions during the structure refactor."""

from .entity_not_found_error import EntityNotFoundError

class ReportNotFoundError(EntityNotFoundError):
    """
    يوضح أن تقرير المراقبة الذي يعتمد عليه التحليل غير موجود.
    """
    def __init__(self, report_id: int) -> None:
        """ينشئ رسالة تربط الفشل بمعرف تقرير المراقبة المطلوب."""
        super().__init__(
            f"Monitoring report with id "
            f"{report_id} was not found."
        )
