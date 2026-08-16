"""
جزء من Claude Runtime لبناء العملية أو تشغيل الجلسة أو قراءة stream أو تسجيل job.

الموقع في المعمارية: Claude supervisory runtime.
يُستدعى بواسطة: composition أو Scheduler.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: Claude/Ollama للـreasoning/model؛ policy والحفظ والتنفيذ الحتمي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
class ClaudeRuntimeError(RuntimeError):
    """Base error for controlled Claude runtime failures."""


class ClaudeStructuredOutputError(ClaudeRuntimeError):
    """Raised when Claude returns output outside the accepted contract."""


class ClaudeToolAccessError(ClaudeRuntimeError):
    """Raised when a request asks for tools that are not enabled."""


class ClaudeProcessExecutionError(ClaudeRuntimeError):
    """Raised when the external Claude process cannot execute cleanly."""


class ClaudeProcessOutputError(ClaudeRuntimeError):
    """Raised when Claude process JSON output is outside its envelope."""
