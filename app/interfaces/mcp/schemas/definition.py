"""
نماذج عقود MCP الداخلية.

تصف تعريف الأداة واستدعاءها ونتيجتها، وتتحقق من المعرفات والوسائط والحمولات
قبل أن تدخل إلى حدود الأدوات أو تخرج منها.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)


@dataclass(slots=True, frozen=True)
class ProjectToolDefinition:
    """
    يمثل تعريف أداة MCP ووسائطها ووصف نتيجة استخدامها.
    """
    tool_id: str
    description: str
    input_schema: dict[str, Any]
    read_only: bool = True

    def __post_init__(self) -> None:
        """
        يتحقق من صحة اسم تعريف الأداة ووصفها ومخطط وسائطها قبل التسجيل.
        """
        if not self.tool_id.strip():
            raise ValueError(
                "tool_id must not be empty."
            )

        if not self.description.strip():
            raise ValueError(
                "description must not be empty."
            )

