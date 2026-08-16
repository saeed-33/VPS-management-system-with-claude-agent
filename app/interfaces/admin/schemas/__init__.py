"""
مخططات واجهة الإدارة.

تجمع نماذج الطلبات والاستجابات التي تثبت شكل البيانات المتبادلة عبر API قبل
تمريرها إلى عقود وخدمات المجال.
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