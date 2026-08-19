"""Class extracted from exceptions during the structure refactor."""

from .entity_not_found_error import EntityNotFoundError

class SpecialistDefinitionNotFoundError(
    EntityNotFoundError
):
    """
    يوضح أن تعريف المتخصص المطلوب للتحقيق غير موجود.
    """
    def __init__(self, specialist_id: int) -> None:
        """ينشئ رسالة تربط الفشل بمعرف تعريف المتخصص."""
        super().__init__(
            f"Specialist definition with id "
            f"{specialist_id} was not found."
        )
