"""Class extracted from diagnostic_tools during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import ipaddress

import re

import shlex

from types import MappingProxyType

from typing import Any, Mapping

from .diagnostic_tool_call import DiagnosticToolCall

from .diagnostic_tool_definition import DiagnosticToolDefinition

class DiagnosticToolRegistry:
    """
    سجل الأدوات التي يمكن للتحقيق اكتشافها واستدعاؤها بعد التحقق.
    """
    def __init__(
        self,
        definitions: tuple[
            DiagnosticToolDefinition,
            ...
        ],
    ) -> None:
        """
        يبني فهرس الأدوات بمعرفات موحدة ويرفض المعرفات المكررة أو الفارغة.
        """
        by_id: dict[
            str,
            DiagnosticToolDefinition,
        ] = {}

        for definition in definitions:
            tool_id = (
                definition.tool_id
                .strip()
                .casefold()
            )

            if not tool_id:
                raise ValueError(
                    "Diagnostic tool ID must not be empty."
                )

            if tool_id in by_id:
                raise ValueError(
                    f"Duplicate diagnostic tool ID: {tool_id}"
                )

            if definition.timeout_seconds <= 0:
                raise ValueError(
                    f"{tool_id}: timeout_seconds must be > 0."
                )

            if definition.output_limit_chars < 100:
                raise ValueError(
                    f"{tool_id}: output_limit_chars must be >= 100."
                )

            by_id[tool_id] = definition

        self._definitions = tuple(
            sorted(
                by_id.values(),
                key=lambda item: item.tool_id,
            )
        )
        self._by_id = MappingProxyType(
            by_id
        )

    @property
    def definitions(
        self,
    ) -> tuple[
        DiagnosticToolDefinition,
        ...
    ]:
        """
        يعيد تعريفات الأدوات المسجلة لتعرضها واجهة التحقيق أو تستخدمها السياسة.
        """
        return self._definitions

    def get(
        self,
        tool_id: str,
    ) -> DiagnosticToolDefinition | None:
        """
        يبحث عن أداة بالمعرف دون اختلاق تعريف عند غيابها.
        """
        return self._by_id.get(
            tool_id.strip().casefold()
        )

    def require(
        self,
        tool_id: str,
    ) -> DiagnosticToolDefinition:
        """
        يسترجع أداة مسجلة أو يرفع خطأ واضحًا عند طلب أداة غير معروفة.
        """
        definition = self.get(tool_id)

        if definition is None:
            raise LookupError(
                f"Unknown diagnostic tool: {tool_id}"
            )

        return definition

    def allowed_for_specialist(
        self,
        allowed_tool_ids: tuple[str, ...],
    ) -> tuple[
        DiagnosticToolDefinition,
        ...
    ]:
        """
        يعيد الأدوات التي تناسب مجالات المتخصص وقائمة أدواته المسموحة.
        """
        result = []

        for tool_id in allowed_tool_ids:
            definition = self.require(
                tool_id
            )

            if definition not in result:
                result.append(definition)

        return tuple(result)

    def render_call(
        self,
        call: DiagnosticToolCall,
        *,
        allowed_tool_ids: tuple[str, ...],
    ) -> str:
        """
        يتحقق من طلب الأداة ويحول معاملاته إلى أمرها المسجل.
        """
        allowed = {
            value.strip().casefold()
            for value in allowed_tool_ids
            if value.strip()
        }

        normalized_id = (
            call.tool_id
            .strip()
            .casefold()
        )

        if normalized_id not in allowed:
            raise PermissionError(
                f"Tool is not allowed for this Specialist: "
                f"{normalized_id}"
            )

        return self.require(
            normalized_id
        ).render_command(
            call.arguments
        )
