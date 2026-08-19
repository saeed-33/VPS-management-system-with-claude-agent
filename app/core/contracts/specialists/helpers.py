"""عقود تعريف المتخصصين الذين يحققون في مجالات مختلفة من عطل السيرفر."""

from __future__ import annotations

from dataclasses import dataclass, field

import re

_SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,99}$")

def validate_specialist_slug(value: str) -> None:
    """
    يتحقق من أن معرف المتخصص النصي صالح وثابت للاستخدام في التوجيه والتخزين.

    يضمن النمط الموحد أن يبقى المعرف آمنًا للروابط والسجلات ولا يتغير بسبب
    اختلاف حالة الأحرف أو إدخال رموز غير متوقعة.
    """
    if not _SLUG_PATTERN.fullmatch(value):
        raise ValueError(
            "Specialist slug must start with a lowercase letter and contain only lowercase letters, digits, '-' or '_'."
        )
