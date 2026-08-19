"""Class extracted from exceptions during the structure refactor."""

from .application_error import ApplicationError

class InvalidOperationError(ApplicationError):
    """
    يوضح أن الطلب مفهوم لكنه يخالف حالة المجال الحالية.
    """
