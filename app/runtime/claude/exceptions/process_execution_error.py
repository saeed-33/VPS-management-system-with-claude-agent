"""استثناءات تشغيل Claude."""

from .runtime_error import ClaudeRuntimeError

class ClaudeProcessExecutionError(ClaudeRuntimeError):
    """
    خطأ يصف عدم قدرة النظام على إنشاء عملية Claude أو تشغيلها.
    """

