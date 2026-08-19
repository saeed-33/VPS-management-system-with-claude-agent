"""Router لمسارات ملفات المراقبة."""

from fastapi import APIRouter

router = APIRouter(
    tags=["monitoring profiles"],
)

# Import route modules after creating the shared router. Each module registers
# its endpoints on this object, keeping one public router facade for app.main.
from . import assignments as _assignments  # noqa: E402,F401
from . import read as _read  # noqa: E402,F401
from . import write as _write  # noqa: E402,F401
