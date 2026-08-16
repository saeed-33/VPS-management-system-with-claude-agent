"""
جزء من واجهة الإدارة يعرّف route أو payload أو عرضًا للمشغل.

الموقع في المعمارية: Administration interface.
يُستدعى بواسطة: FastAPI أو متصفح الإدارة.
يعتمد مباشرة على: app.interfaces.admin.schemas.commands، app.interfaces.admin.schemas.reports، app.interfaces.admin.schemas.servers.
الحد المعماري: العرض والتحقق الشكلي لا يمنحان صلاحية تنفيذ؛ authorization في الخدمة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from app.interfaces.admin.schemas.commands import (
    AssignCommandRequest,
    CommandCreateRequest,
    CommandResponse,
    CommandUpdateRequest,
    ServerCommandAssignmentResponse,
    UpdateCommandAssignmentRequest,
)
from app.interfaces.admin.schemas.reports import (
    CommandExecutionResponse,
    PaginatedReportsResponse,
    ReportDetailsResponse,
    ReportListItemResponse,
)
from app.interfaces.admin.schemas.servers import (
    ServerCreateRequest,
    ServerResponse,
    ServerUpdateRequest,
    SSHTestResponse,
)

__all__ = [
    "ServerCreateRequest",
    "ServerUpdateRequest",
    "ServerResponse",
    "SSHTestResponse",
    "CommandCreateRequest",
    "CommandUpdateRequest",
    "CommandResponse",
    "AssignCommandRequest",
    "UpdateCommandAssignmentRequest",
    "ServerCommandAssignmentResponse",
    "ReportListItemResponse",
    "CommandExecutionResponse",
    "ReportDetailsResponse",
    "PaginatedReportsResponse",
]