"""
نماذج عقود MCP الداخلية.

تصف تعريف الأداة واستدعاءها ونتيجتها، وتتحقق من المعرفات والوسائط والحمولات
قبل أن تدخل إلى حدود الأدوات أو تخرج منها.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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


@dataclass(slots=True, frozen=True)
class ProjectToolResult:
    """
    يمثل نتيجة الأداة مع النجاح أو الخطأ والحمولة القابلة للتسلسل.
    """
    tool_id: str
    success: bool
    data: dict[str, Any] = field(
        default_factory=dict
    )
    error_code: str | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        """
        يتحقق من اتساق النجاح أو الخطأ والحمولة القابلة للتسلسل في النتيجة.
        """
        if not self.tool_id.strip():
            raise ValueError(
                "tool_id must not be empty."
            )

        if self.success:
            if self.error_code is not None:
                raise ValueError(
                    "successful tool result cannot "
                    "have error_code."
                )
            if self.error_message is not None:
                raise ValueError(
                    "successful tool result cannot "
                    "have error_message."
                )
