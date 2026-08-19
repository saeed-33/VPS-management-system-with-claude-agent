"""Class extracted from exceptions during the structure refactor."""

from .duplicate_entity_error import DuplicateEntityError

class DuplicateMonitoringProfileError(
    DuplicateEntityError
):
    """
    يوضح أن اسم ملف المراقبة مستخدم مسبقًا.
    """
    def __init__(self, name: str) -> None:
        """ينشئ رسالة تربط التعارض باسم ملف المراقبة المكرر."""
        super().__init__(
            f"A monitoring profile named "
            f"'{name}' already exists."
        )
