"""تعارض تشغيلي بين تقريرين."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(slots=True, frozen=True)
class CompatibilityConflict:
    """
    يمثل اختلافًا محددًا بين قيمة التقرير الحالي والقيمة التاريخية مع أمر اختياري.
    """
    field: str
    current: Any
    historical: Any
    command_id: int | None = None
