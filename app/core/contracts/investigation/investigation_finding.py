"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

@dataclass(slots=True, frozen=True)
class InvestigationFinding:
    """
    نتيجة مثبتة نسبيًا يخرج بها التحقيق مع مستوى ثقة ومراجعها.

    يحتفظ العقد بالأدلة المساندة ومصادر المعرفة والأدلة الناقصة حتى يعرف قارئ
    التشخيص ما الذي ثبت وما الذي ما زال يحتاج فحصًا.
    """
    finding_id: str
    title: str
    description: str
    confidence: float
    evidence_ids: tuple[str, ...] = ()
    knowledge_source_ids: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """يتحقق من هوية النتيجة ونصها وأن الثقة ضمن المجال المعروف."""
        if not self.finding_id.strip():
            raise ValueError(
                "finding_id must not be empty."
            )
        if not self.title.strip():
            raise ValueError(
                "Finding title must not be empty."
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Finding confidence must be between 0 and 1."
            )
