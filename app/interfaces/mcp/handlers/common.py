"""
أدوات التحقق المشترك لمعالجات MCP.

تقرأ الوسائط المطلوبة والاختيارية من طلب الأداة وتتحقق من أنواعها، كما تضمن
توفر الاعتماديات المطلوبة قبل تنفيذ المعالج.
"""
from __future__ import annotations

from typing import Any


class BoundaryCommonMixin:
    """
    يوفر تحقق الوسائط والاعتماديات المشترك لكل حدود الأدوات.
    """
    @staticmethod
    def _required_int(
        arguments: dict[str, Any],
        name: str,
    ) -> int:
        """
        يقرأ وسيطًا صحيحًا مطلوبًا ويرفض النوع أو الغياب برسالة MCP واضحة.
        """
        value = arguments.get(
            name
        )

        if not isinstance(value, int):
            raise ValueError(
                f"{name} must be an integer."
            )

        if value < 1:
            raise ValueError(
                f"{name} must be >= 1."
            )

        return value

    @staticmethod
    def _required_string(
        arguments: dict[str, Any],
        name: str,
    ) -> str:
        """
        يقرأ نصًا مطلوبًا غير فارغ من وسائط الأداة.
        """
        value = arguments.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{name} must be a non-empty string."
            )
        return value.strip()

    @staticmethod
    def _required_string_list(
        arguments: dict[str, Any],
        name: str,
    ) -> list[str]:
        """
        يقرأ قائمة نصوص مطلوبة ويتحقق من عناصرها.
        """
        value = arguments.get(name)
        if not isinstance(value, list) or not value:
            raise ValueError(
                f"{name} must be a non-empty list."
            )
        result: list[str] = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise ValueError(
                    f"{name} must contain strings."
                )
            result.append(item.strip())
        return result

    @staticmethod
    def _optional_int(
        arguments: dict[str, Any],
        name: str,
        *,
        default: int,
    ) -> int:
        """
        يقرأ وسيطًا صحيحًا اختياريًا مع قيمة افتراضية مناسبة.
        """
        value = arguments.get(
            name,
            default,
        )

        if not isinstance(value, int):
            raise ValueError(
                f"{name} must be an integer."
            )

        if value < 1:
            raise ValueError(
                f"{name} must be >= 1."
            )

        return value

    @staticmethod
    def _require_dependency(
        dependency,
        name: str,
    ) -> None:
        """
        يتحقق من توفر اعتماد boundary قبل استخدامه في تنفيذ الأداة.
        """
        if dependency is None:
            raise ValueError(
                f"{name} is not configured."
            )
