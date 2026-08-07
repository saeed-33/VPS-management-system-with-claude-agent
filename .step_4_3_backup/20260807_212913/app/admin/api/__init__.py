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
]