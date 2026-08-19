"""استثناءات تشغيل Claude."""

from .runtime_error import ClaudeRuntimeError

class ClaudeToolAccessError(ClaudeRuntimeError):
    """
    خطأ يوضح أن الجلسة طلبت أدوات تشغيلية دون تفعيل صلاحيتها.
    """

