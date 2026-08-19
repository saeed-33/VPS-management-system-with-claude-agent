"""Class extracted from diagnostic_tools during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import ipaddress

import re

import shlex

from types import MappingProxyType

from typing import Any, Mapping

from .diagnostic_tool_parameter import DiagnosticToolParameter

from .diagnostic_tool_risk import DiagnosticToolRisk

@dataclass(slots=True, frozen=True)
class DiagnosticToolDefinition:
    """
    تعريف أداة قراءة يتضمن مجالاتها ومعاملاتها وقالب أمرها وحدودها.
    """
    tool_id: str
    name: str
    description: str
    domains: tuple[str, ...]
    parameters: tuple[DiagnosticToolParameter, ...]
    command_template: tuple[str, ...]
    timeout_seconds: float
    requires_sudo: bool = False
    risk: DiagnosticToolRisk = DiagnosticToolRisk.READ_ONLY
    output_limit_chars: int = 20_000
    metadata: Mapping[str, Any] = MappingProxyType({})

    def render_command(
        self,
        arguments: Mapping[str, Any] | None = None,
    ) -> str:
        """
        يملأ قالب أداة التشخيص بقيم متحقق منها ويعيد أمرًا مضبوطًا قابلًا للتنفيذ.
        """
        raw = dict(arguments or {})
        known = {
            item.name
            for item in self.parameters
        }

        unknown = set(raw) - known

        if unknown:
            raise ValueError(
                "Unknown tool parameters: "
                + ", ".join(sorted(unknown))
            )

        values: dict[str, Any] = {}

        for parameter in self.parameters:
            values[parameter.name] = parameter.validate(
                raw.get(parameter.name)
            )

        tokens: list[str] = []

        if self.requires_sudo:
            tokens.extend(
                ["sudo", "-n"]
            )

        for token in self.command_template:
            if (
                token.startswith("{")
                and token.endswith("}")
            ):
                key = token[1:-1]

                if key not in values:
                    raise ValueError(
                        f"Unknown command placeholder: {key}"
                    )

                value = values[key]

                if value is None:
                    continue

                tokens.append(str(value))
            else:
                tokens.append(token)

        return shlex.join(tokens)
