"""Class extracted from diagnostic_tools during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import ipaddress

import re

import shlex

from types import MappingProxyType

from typing import Any, Mapping

from .diagnostic_parameter_kind import DiagnosticParameterKind

from .constants import _SAFE_NAME_RE

from .constants import _SAFE_PATH_RE

@dataclass(slots=True, frozen=True)
class DiagnosticToolParameter:
    """
    تعريف معامل أداة تشخيص مع نوعه وحدوده وقيمته الافتراضية.
    """
    name: str
    kind: DiagnosticParameterKind
    required: bool = True
    default: Any = None
    minimum: int | None = None
    maximum: int | None = None
    description: str | None = None

    def validate(self, value: Any) -> Any:
        """
        يتحقق من قيمة المعامل ونوعها وحدودها ويمنع أسماء الخدمات والمسارات غير الآمنة.
        """
        if value is None:
            if self.required and self.default is None:
                raise ValueError(
                    f"Missing required parameter: {self.name}"
                )
            return self.default

        if self.kind == DiagnosticParameterKind.INTEGER:
            if isinstance(value, bool):
                raise ValueError(
                    f"{self.name} must be an integer."
                )
            try:
                normalized = int(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{self.name} must be an integer."
                ) from exc

            if (
                self.minimum is not None
                and normalized < self.minimum
            ):
                raise ValueError(
                    f"{self.name} must be >= {self.minimum}."
                )

            if (
                self.maximum is not None
                and normalized > self.maximum
            ):
                raise ValueError(
                    f"{self.name} must be <= {self.maximum}."
                )

            return normalized

        if self.kind == DiagnosticParameterKind.PORT:
            try:
                port = int(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{self.name} must be a TCP/UDP port."
                ) from exc

            if not 1 <= port <= 65535:
                raise ValueError(
                    f"{self.name} must be between 1 and 65535."
                )

            return port

        if not isinstance(value, str):
            raise ValueError(
                f"{self.name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{self.name} must not be empty."
            )

        if self.kind == DiagnosticParameterKind.SERVICE:
            if not _SAFE_NAME_RE.fullmatch(normalized):
                raise ValueError(
                    f"Unsafe service name: {normalized!r}"
                )
            return normalized

        if self.kind == DiagnosticParameterKind.TEXT_TOKEN:
            if not _SAFE_NAME_RE.fullmatch(normalized):
                raise ValueError(
                    f"Unsafe token: {normalized!r}"
                )
            return normalized

        if self.kind == DiagnosticParameterKind.PATH:
            if not _SAFE_PATH_RE.fullmatch(normalized):
                raise ValueError(
                    f"Unsafe absolute path: {normalized!r}"
                )
            if ".." in normalized.split("/"):
                raise ValueError(
                    "Path traversal is not allowed."
                )
            return normalized

        if self.kind == DiagnosticParameterKind.HOST:
            try:
                ipaddress.ip_address(normalized)
                return normalized
            except ValueError:
                pass

            if (
                len(normalized) > 253
                or not re.fullmatch(
                    r"[A-Za-z0-9.-]+",
                    normalized,
                )
            ):
                raise ValueError(
                    f"Unsafe host value: {normalized!r}"
                )

            return normalized.casefold()

        raise ValueError(
            f"Unsupported parameter kind: {self.kind}"
        )
