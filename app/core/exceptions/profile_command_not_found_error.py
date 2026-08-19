"""Class extracted from exceptions during the structure refactor."""

from .entity_not_found_error import EntityNotFoundError

class ProfileCommandNotFoundError(
    EntityNotFoundError
):
    """
    يوضح أن أمر المراقبة غير مرتبط بملف المراقبة المطلوب.
    """
    def __init__(
        self,
        profile_id: int,
        command_id: int,
    ) -> None:
        """ينشئ رسالة تربط الفشل بمعرفي الملف والأمر."""
        super().__init__(
            f"Command {command_id} is not assigned "
            f"to monitoring profile {profile_id}."
        )
