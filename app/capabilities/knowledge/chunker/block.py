"""كتلة داخلية قبل إنشاء مقطع المعرفة."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class _Block:
    """
    يمثل كتلة نصية مرتبطة بعنوان قسم ورقم صفحة قبل دمجها في مقطع نهائي.
    """
    text: str
    section_title: str | None
    page_number: int | None
