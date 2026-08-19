"""Class extracted from exceptions during the structure refactor."""

from .application_error import ApplicationError

class EntityNotFoundError(ApplicationError):
    """
    أساس أخطاء البحث عندما لا يجد التطبيق سجلًا تحتاجه العملية الحالية.
    """
