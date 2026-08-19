"""
نماذج عقود MCP الداخلية.

تصف تعريف الأداة واستدعاءها ونتيجتها، وتتحقق من المعرفات والوسائط والحمولات
قبل أن تدخل إلى حدود الأدوات أو تخرج منها.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class ProjectToolCall:
    """
    يمثل طلب استدعاء أداة باسمها ووسائطها.
    """
    tool_id: str
    arguments: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        يتحقق من اسم الأداة ووسائط الاستدعاء قبل توجيه الطلب.
        """
        if not self.tool_id.strip():
            raise ValueError(
                "tool_id must not be empty."
            )
