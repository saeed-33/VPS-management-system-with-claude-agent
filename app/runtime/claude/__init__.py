"""
جزء من Claude Runtime لبناء العملية أو تشغيل الجلسة أو قراءة stream أو تسجيل job.

الموقع في المعمارية: Claude supervisory runtime.
يُستدعى بواسطة: composition أو Scheduler.
يعتمد مباشرة على: app.runtime.claude.job_service، app.runtime.claude.models، app.runtime.claude.native_monitoring، app.runtime.claude.runtime، app.runtime.claude.session_runner، app.runtime.claude.supervisor.
الحد المعماري: Claude/Ollama للـreasoning/model؛ policy والحفظ والتنفيذ الحتمي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from app.runtime.claude.job_service import (
    ClaudeAgentJobService,
)
from app.runtime.claude.models import (
    ClaudeJobStatus,
    ClaudeRawResult,
    ClaudeRuntimeRequest,
    ClaudeRuntimeResult,
    ClaudeStructuredOutput,
)
from app.runtime.claude.native_monitoring import (
    ClaudeNativeMonitoringRunner,
)
from app.runtime.claude.runtime import (
    ClaudeRuntimeAdapter,
    ClaudeSessionRunner,
)
from app.runtime.claude.session_runner import (
    ClaudeCliJsonDecoder,
    ClaudeProcessCommand,
    ClaudeProcessCommandBuilder,
    SubprocessClaudeSessionRunner,
)
from app.runtime.claude.supervisor import (
    ClaudeSupervisor,
)


__all__ = [
    "ClaudeAgentJobService",
    "ClaudeCliJsonDecoder",
    "ClaudeJobStatus",
    "ClaudeNativeMonitoringRunner",
    "ClaudeProcessCommand",
    "ClaudeProcessCommandBuilder",
    "ClaudeRawResult",
    "ClaudeRuntimeAdapter",
    "ClaudeRuntimeRequest",
    "ClaudeRuntimeResult",
    "ClaudeSessionRunner",
    "ClaudeStructuredOutput",
    "ClaudeSupervisor",
    "SubprocessClaudeSessionRunner",
]
