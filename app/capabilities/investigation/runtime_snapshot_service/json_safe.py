"""تحويل القيم المعقدة إلى قيم قابلة للتسلسل بصيغة JSON."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

class JsonSafeValueConverter:
    def convert(
        self,
        value: Any,
    ) -> Any:
        """
        يحسب أو يجهز قيمة داخلية لمسار التحقيق (json safe).
        """
        if value is None:
            return None

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ):
            return value

        if isinstance(value, dict):
            return {
                str(key): self.convert(
                    item
                )
                for key, item
                in value.items()
            }

        if isinstance(
            value,
            (list, tuple, set),
        ):
            return [
                self.convert(item)
                for item in value
            ]

        if hasattr(value, "value"):
            return self.convert(
                value.value
            )

        if hasattr(
            value,
            "isoformat",
        ):
            try:
                return value.isoformat()
            except Exception:
                pass

        try:
            return self.convert(
                asdict(value)
            )
        except (
            TypeError,
            ValueError,
        ):
            return str(value)
