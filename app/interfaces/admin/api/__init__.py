"""
حزمة مسارات API الإدارية.

تجمع نقاط HTTP التي تعرض وظائف التحقيق والمعرفة والمعالجة والتشخيص والنظام،
وتبقي التحقق من الهوية والصلاحية في طبقات الاعتماديات والمصادقة.
"""
from app.interfaces.admin.api.agent_observability import (
    router as agent_observability_router,
)
from app.interfaces.admin.api.investigations import (
    router as investigations_router,
)
from app.interfaces.admin.api.knowledge_sources import (
    router as knowledge_sources_router,
)
from app.interfaces.admin.api.diagnostic_tools import (
    router as diagnostic_tools_router,
)
from app.interfaces.admin.api.system import (
    router as system_router,
)
from app.interfaces.admin.api.specialists import (
    router as specialists_router,
)
from app.interfaces.admin.api.commands import (
    router as commands_router,
)
from app.interfaces.admin.api.reports import (
    router as reports_router,
)
from app.interfaces.admin.api.servers import (
    router as servers_router,
)
from app.interfaces.admin.api.profiles import (
    router as profiles_router,
)
from app.interfaces.admin.api.remediation import (
    router as remediation_router,
)
from app.interfaces.admin.api.autonomous_remediation import (
    router as autonomous_remediation_router,
)

__all__ = [
    "agent_observability_router",
    "investigations_router",
    "servers_router",
    "commands_router",
    "reports_router",
    "profiles_router",
    "specialists_router",
    "knowledge_sources_router",
    "diagnostic_tools_router",
    "system_router",
    "remediation_router",
    "autonomous_remediation_router",
]
