"""استثناءات تشغيل Claude."""

from .runtime_error import ClaudeRuntimeError

class ClaudeProcessOutputError(ClaudeRuntimeError):
    """
    خطأ يصف مخرجًا فارغًا أو غير صالح أو لا يثبت اكتمال جلسة Claude.
    """

