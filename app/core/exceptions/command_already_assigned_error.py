"""Class extracted from exceptions during the structure refactor."""

from .invalid_operation_error import InvalidOperationError

class CommandAlreadyAssignedError(
    InvalidOperationError
):
    """
    يوضح أن أمر المراقبة مرتبط بالسيرفر نفسه مسبقًا.
    """
    def __init__(
        self,
        server_id: int,
        command_id: int,
    ) -> None:
        """ينشئ رسالة تربط التعارض بمعرفي السيرفر والأمر."""
        super().__init__(
            f"Command {command_id} is already assigned "
            f"to server {server_id}."
        )
