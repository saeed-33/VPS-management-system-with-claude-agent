"""
عقود بيانات مصادر المعرفة.

تحدد نماذج إنشاء وتعديل المصدر وقواعد تطبيع القوائم والتحقق من نوع المصدر
ومحتواه قبل وصول البيانات إلى الخدمات والمستودعات.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_ALLOWED_SOURCE_TYPES = {
    "url",
    "file",
    "inline",
}

def _normalize_list(
    values: list[str] | tuple[str, ...],
    *,
    lowercase: bool = True,
) -> tuple[str, ...]:
    """
    يطبع قائمة نصية ويزيل القيم الفارغة والمكررة قبل تخزينها.
    """
    result: list[str] = []
    seen: set[str] = set()

    for raw in values:
        if not isinstance(raw, str):
            raise ValueError(
                "Knowledge source list values must be strings."
            )

        value = raw.strip()

        if not value:
            continue

        if lowercase:
            value = value.casefold()

        key = value.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(value)

    return tuple(result)
