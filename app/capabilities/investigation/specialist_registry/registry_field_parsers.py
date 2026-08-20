"""
سجل الاختصاصيين وتعريفاتهم التشغيلية.

يطبع السجل تعريفات الاختصاصيين المفعلة، ويفهرس مجالاتها، ويوفر مطابقة مفردة
ومتعددة مع ترتيب ثابت وبيانات تغطية قابلة للتدقيق.
"""

from __future__ import annotations

from dataclasses import dataclass

from types import MappingProxyType

from typing import Any, Iterable, Mapping

from app.core.contracts.specialists.helpers import validate_specialist_slug

from .specialist_registry_validation_error import SpecialistRegistryValidationError

def _token(value: str) -> str:
    """
    يطبع رمز مجال أو وسم للمقارنة.
    """
    return value.strip().casefold()

def _string_tuple(values: Any, field_name: str, lowercase: bool = False) -> tuple[str, ...]:
    """
    يحوّل قائمة القيم إلى tuple نصية مطبعة.
    """
    if not isinstance(values, list):
        raise SpecialistRegistryValidationError(
            f"{field_name} must be a JSON list."
        )

    result: list[str] = []
    seen: set[str] = set()

    for raw in values:
        if not isinstance(raw, str):
            raise SpecialistRegistryValidationError(
                f"{field_name} must contain strings only."
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
