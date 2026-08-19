"""Class extracted from exceptions during the structure refactor."""

from .entity_not_found_error import EntityNotFoundError

class ServerNotFoundError(EntityNotFoundError):
    """
    يوضح أن السيرفر المطلوب للمراقبة أو الإدارة غير موجود.
    """
    def __init__(self, server_id: int) -> None:
        """ينشئ رسالة تربط الفشل بمعرف السيرفر المطلوب."""
        super().__init__(
            f"Server with id {server_id} was not found."
        )
