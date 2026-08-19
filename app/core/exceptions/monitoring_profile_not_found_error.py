"""Class extracted from exceptions during the structure refactor."""

from .entity_not_found_error import EntityNotFoundError

class MonitoringProfileNotFoundError(
    EntityNotFoundError
):
    """
    يوضح أن ملف المراقبة المطلوب للسيرفر غير موجود.
    """
    def __init__(self, profile_id: int) -> None:
        """ينشئ رسالة تربط الفشل بمعرف ملف المراقبة المطلوب."""
        super().__init__(
            f"Monitoring profile with id "
            f"{profile_id} was not found."
        )
