"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.infrastructure.database.repositories.specialist_definition_repository، app.infrastructure.database.repositories.command_repository، app.infrastructure.database.repositories.report_repository، app.infrastructure.database.repositories.server_repository.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from app.infrastructure.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)
from app.infrastructure.database.repositories.command_repository import (
    CommandRepository,
)
from app.infrastructure.database.repositories.report_repository import (
    ReportRepository,
)
from app.infrastructure.database.repositories.server_repository import (
    ServerRepository,
)

__all__ = [
    "ServerRepository",
    "CommandRepository",
    "ReportRepository",
    "SpecialistDefinitionRepository",
]