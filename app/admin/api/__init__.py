from app.admin.api.knowledge_sources import (
    router as knowledge_sources_router,
)
from app.admin.api.specialists import (
    router as specialists_router,
)
from app.admin.api.commands import (
    router as commands_router,
)
from app.admin.api.reports import (
    router as reports_router,
)
from app.admin.api.servers import (
    router as servers_router,
)
from app.admin.api.profiles import (
    router as profiles_router,
)

__all__ = [
    "servers_router",
    "commands_router",
    "reports_router",
    "profiles_router",
    "specialists_router",
    "knowledge_sources_router",
]