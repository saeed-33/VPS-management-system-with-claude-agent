"""Class extracted from exceptions during the structure refactor."""

from .application_error import ApplicationError

class DuplicateEntityError(ApplicationError):
    """
    أساس أخطاء محاولة إنشاء سجل يملك هوية مستخدمة مسبقًا.
    """
