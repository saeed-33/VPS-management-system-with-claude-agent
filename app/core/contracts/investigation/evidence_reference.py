"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

from .evidence_kind import EvidenceKind

@dataclass(slots=True, frozen=True)
class EvidenceReference:
    """
    مرجع قابل للتتبع إلى دليل جمعه التحقيق أو ورثه من مرحلة سابقة.

    يربط المعرف والعنوان والنوع والمصدر والاقتباس ما سيقرأه التشخيص بما قيس
    فعليًا أو استُرجع من مصدر معروف.
    """
    evidence_id: str
    kind: EvidenceKind
    title: str
    source_id: int | str | None = None
    excerpt: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """يتحقق من وجود معرف وعنوان يمكن الرجوع إليهما في سجل التحقيق."""
        if not self.evidence_id.strip():
            raise ValueError(
                "evidence_id must not be empty."
            )
        if not self.title.strip():
            raise ValueError(
                "Evidence title must not be empty."
            )
