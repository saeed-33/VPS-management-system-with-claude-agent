"""عقد يحدد موضع الدليل داخل ملف أو مخرج أو وظيفة مرتبطة بالتحقيق."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceLocation:
    """
    موقع قابل للتتبع يشرح أين ظهرت المعلومة التي استند إليها التحقيق.

    يجمع الملف والسطر والمصدر والسبب ومعرفات الأدلة حتى يستطيع المراجع العودة
    إلى أصل الاستنتاج بدل الاكتفاء بنصه المختصر.
    """

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
        """يتحقق من وجود مصدر وسبب وموقع سطر صالح للدليل."""
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
        يحول موضع الدليل إلى بيانات قابلة للحفظ أو الإرسال إلى واجهة العرض.

        يحول مجموعة معرفات الأدلة إلى قائمة حتى يبقى شكل الرد مناسبًا للتخزين
        وواجهات JSON.
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
