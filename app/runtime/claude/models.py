"""
نماذج البيانات التي تصف طلب جلسة Claude ونتيجتها وحالتها.

تمنع هذه النماذج انتقال طلب ناقص أو نتيجة غير قابلة للتفسير إلى بقية رحلة
المراقبة، وتفصل بين المخرجات الخام والنتيجة المنظمة والحالة المحفوظة.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ClaudeJobStatus(StrEnum):
    """
    الحالات المسموح بها لدورة مهمة Claude منذ الانتظار حتى النهاية.
    """
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"


@dataclass(slots=True, frozen=True)
class ClaudeRuntimeRequest:
    """
    طلب يحدد نوع مهمة Claude وسياقها ووقتها وأدواتها المسموح بها.
    """
    job_id: str
    job_type: str
    prompt: str
    context: dict[str, Any] = field(
        default_factory=dict
    )
    timeout_seconds: float = 60.0
    max_turns: int = 8
    allowed_tools: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        يتحقق من هوية المهمة ونصها وحدودها وأسماء الأدوات قبل السماح بتشغيلها.
        """
        if not self.job_id.strip():
            raise ValueError(
                "job_id must not be empty."
            )

        if not self.job_type.strip():
            raise ValueError(
                "job_type must not be empty."
            )

        if not self.prompt.strip():
            raise ValueError(
                "prompt must not be empty."
            )

        if self.timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be > 0."
            )

        if self.max_turns < 1:
            raise ValueError(
                "max_turns must be >= 1."
            )

        for tool_id in self.allowed_tools:
            if not tool_id.strip():
                raise ValueError(
                    "allowed_tools cannot contain empty IDs."
                )


@dataclass(slots=True, frozen=True)
class ClaudeRawResult:
    """
    المخرج الخام الذي تعيده الجلسة مع معرفها وعدد جولاتها وأدواتها.
    """
    session_id: str
    content: str
    turn_count: int = 0
    tool_call_count: int = 0
    usage_metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        يتحقق من وجود معرف ومحتوى للجلسة ومن عدم سلبية عداداتها.
        """
        if not self.session_id.strip():
            raise ValueError(
                "session_id must not be empty."
            )

        if not self.content.strip():
            raise ValueError(
                "content must not be empty."
            )

        if self.turn_count < 0:
            raise ValueError(
                "turn_count must be >= 0."
            )

        if self.tool_call_count < 0:
            raise ValueError(
                "tool_call_count must be >= 0."
            )


@dataclass(slots=True, frozen=True)
class ClaudeStructuredOutput:
    """
    النتيجة التي فكها النظام من مخرج Claude وتحتوي الحالة والملخص والبيانات.
    """
    status: ClaudeJobStatus
    summary: str
    data: dict[str, Any] = field(
        default_factory=dict
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        يتأكد أن النتيجة تحمل حالة نهائية وملخصًا يمكن حفظه وعرضه.
        """
        if self.status not in {
            ClaudeJobStatus.COMPLETED,
            ClaudeJobStatus.FAILED,
            ClaudeJobStatus.CANCELLED,
        }:
            raise ValueError(
                "structured status must be completed, "
                "failed, or cancelled."
            )

        if not self.summary.strip():
            raise ValueError(
                "summary must not be empty."
            )


@dataclass(slots=True, frozen=True)
class ClaudeRuntimeResult:
    """
    النتيجة النهائية القابلة للحفظ لمهمة Claude، بما فيها الفشل أو المهلة ومؤشرات الاستخدام.
    """
    job_id: str
    job_type: str
    status: ClaudeJobStatus
    session_id: str | None = None
    structured_output: ClaudeStructuredOutput | None = None
    error_code: str | None = None
    error_message: str | None = None
    turn_count: int = 0
    tool_call_count: int = 0
    usage_metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        يتحقق من هوية المهمة ونوعها وعدادات النتيجة النهائية قبل تسجيلها.
        """
        if not self.job_id.strip():
            raise ValueError(
                "job_id must not be empty."
            )

        if not self.job_type.strip():
            raise ValueError(
                "job_type must not be empty."
            )

        if self.turn_count < 0:
            raise ValueError(
                "turn_count must be >= 0."
            )

        if self.tool_call_count < 0:
            raise ValueError(
                "tool_call_count must be >= 0."
            )
