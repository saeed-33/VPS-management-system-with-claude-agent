"""
عقود وDTOs مشتركة لنقل البيانات بين الطبقات.

الموقع في المعمارية: Core application contracts.
يُستدعى بواسطة: capabilities وinterfaces وadapters.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا تنفذ I/O أو workflow.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceLocation:
    """A bounded, provenance-bound application error location."""

    file_path: str
    line_number: int
    reason: str
    source: str
    column_number: int | None = None
    module: str | None = None
    function: str | None = None
    exception_type: str | None = None
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not self.file_path.strip():
            raise ValueError("file_path must not be empty.")
        if self.line_number < 1:
            raise ValueError("line_number must be >= 1.")
        if self.column_number is not None and self.column_number < 1:
            raise ValueError("column_number must be >= 1 when provided.")
        if not self.reason.strip():
            raise ValueError("reason must not be empty.")
        if not self.source.strip():
            raise ValueError("source must not be empty.")

    def to_dict(self) -> dict:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

        تُستدعى عندما يصل workflow إلى to_dict؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "module": self.module,
            "function": self.function,
            "exception_type": self.exception_type,
            "reason": self.reason,
            "source": self.source,
            "evidence_ids": list(self.evidence_ids),
        }
