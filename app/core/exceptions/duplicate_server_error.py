"""Class extracted from exceptions during the structure refactor."""

from .duplicate_entity_error import DuplicateEntityError

class DuplicateServerError(DuplicateEntityError):
    """
    يوضح أن اسم السيرفر مستخدم في سجل آخر.
    """
    def __init__(self, name: str) -> None:
        """ينشئ رسالة تربط التعارض باسم السيرفر المكرر."""
        super().__init__(
            f"A server named '{name}' already exists."
        )
