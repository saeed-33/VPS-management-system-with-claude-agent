"""Class extracted from exceptions during the structure refactor."""

from .duplicate_entity_error import DuplicateEntityError

class DuplicateCommandError(DuplicateEntityError):
    """
    يوضح أن اسم أمر المراقبة مستخدم في سجل آخر.
    """
    def __init__(self, name: str) -> None:
        """ينشئ رسالة تربط التعارض باسم أمر المراقبة المكرر."""
        super().__init__(
            f"A monitoring command named "
            f"'{name}' already exists."
        )
