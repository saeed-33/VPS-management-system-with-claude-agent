"""Class extracted from exceptions during the structure refactor."""

from .duplicate_entity_error import DuplicateEntityError

class DuplicateSpecialistDefinitionError(
    DuplicateEntityError
):
    """
    يوضح أن معرف المتخصص النصي مستخدم مسبقًا.
    """
    def __init__(self, slug: str) -> None:
        """ينشئ رسالة تربط التعارض بالمعرف النصي المكرر."""
        super().__init__(
            f"A specialist with slug '{slug}' already exists."
        )
