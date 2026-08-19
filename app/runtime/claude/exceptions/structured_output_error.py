"""استثناءات تشغيل Claude."""

from .runtime_error import ClaudeRuntimeError

class ClaudeStructuredOutputError(ClaudeRuntimeError):
    """
    خطأ يصف مخرجًا من Claude لا يمكن تحويله إلى نتيجة منظمة.
    """

