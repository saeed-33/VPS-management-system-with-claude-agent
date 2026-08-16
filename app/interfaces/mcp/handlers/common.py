"""
حد MCP يكشف Project capabilities لـClaude عبر أدوات typed ومتحقق منها.

الموقع في المعمارية: MCP capability boundary.
يُستدعى بواسطة: Claude أو خادم MCP.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: MCP exposure ليس enforcement أمنيًا مستقلًا؛ التحقق الفعلي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from typing import Any


class BoundaryCommonMixin:
    """
    يمثل BoundaryCommonMixin مسؤولية محددة داخل طبقة MCP capability boundary.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Claude أو خادم MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    @staticmethod
    def _required_int(
        arguments: dict[str, Any],
        name: str,
    ) -> int:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _required_int؛ المدخلات المهمة: arguments، name.
        تعيد int أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _required_string؛ المدخلات المهمة: arguments، name.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _required_string_list؛ المدخلات المهمة: arguments، name.
        تعيد list[str] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _optional_int؛ المدخلات المهمة: arguments، name، default.
        تعيد int أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _require_dependency؛ المدخلات المهمة: dependency، name.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if dependency is None:
            raise ValueError(
                f"{name} is not configured."
            )
