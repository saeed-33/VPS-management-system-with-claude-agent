"""تطبيع النصوص قبل تخزينها أو تقطيعها."""
from __future__ import annotations
from .constants import _BLANKS_RE, _SPACE_RE

def normalize_text(value: str) -> str:
    """
    يوحد فواصل الأسطر والفراغات والأسطر الفارغة في النص قبل تخزينه أو تقطيعه.
    """
    lines = [
        _SPACE_RE.sub(" ", line).strip()
        for line in (
            value
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .split("\n")
        )
    ]

    return _BLANKS_RE.sub(
        "\n\n",
        "\n".join(lines),
    ).strip()
