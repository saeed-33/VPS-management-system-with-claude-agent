from __future__ import annotations

from typing import Any


class BoundaryCommonMixin:
    @staticmethod
    def _required_int(
        arguments: dict[str, Any],
        name: str,
    ) -> int:
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
        if dependency is None:
            raise ValueError(
                f"{name} is not configured."
            )
