"""Class extracted from exceptions during the structure refactor."""

from .entity_not_found_error import EntityNotFoundError

class CommandNotFoundError(EntityNotFoundError):
    """
    يوضح أن فحص المراقبة المطلوب غير موجود.
    """
    def __init__(self, command_id: int) -> None:
        """ينشئ رسالة تربط الفشل بمعرف أمر المراقبة المطلوب."""
        super().__init__(
            f"Monitoring command with id "
            f"{command_id} was not found."
        )
