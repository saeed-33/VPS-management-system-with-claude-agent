"""نتيجة فحص التوافق."""
from __future__ import annotations

from dataclasses import dataclass, field

from .conflict import CompatibilityConflict

@dataclass(slots=True, frozen=True)
class CompatibilityResult:
    """
    يحمل نتيجة فحص التوافق وقائمة التعارضات التي تفسر الرفض عند حدوثه.
    """
    compatible: bool
    conflicts: list[CompatibilityConflict] = field(
        default_factory=list
    )
