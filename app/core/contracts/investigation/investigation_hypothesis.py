"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

@dataclass(slots=True, frozen=True)
class InvestigationHypothesis:
    """
    تفسير محتمل لسبب المشكلة لم يصل بعد إلى مستوى النتيجة المثبتة.

    يميز العقد بين الأدلة التي تدعم الفرضية وتلك التي تناقضها، حتى لا يساوي
    التشخيص بين الاحتمال والدليل.
    """
    hypothesis_id: str
    statement: str
    confidence: float
    supporting_evidence_ids: tuple[str, ...] = ()
    contradicting_evidence_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """يتحقق من هوية الفرضية ونصها وأن مستوى الثقة صالح."""
        if not self.hypothesis_id.strip():
            raise ValueError(
                "hypothesis_id must not be empty."
            )
        if not self.statement.strip():
            raise ValueError(
                "Hypothesis statement must not be empty."
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Hypothesis confidence must be between 0 and 1."
            )
