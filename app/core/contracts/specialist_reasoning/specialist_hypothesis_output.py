"""Contract class extracted from specialist_reasoning.py during the structure refactor."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

class SpecialistHypothesisOutput(BaseModel):
    """
    فرضية متخصصة مع أدلة تؤيدها وأخرى قد تناقضها.
    """
    model_config = ConfigDict(extra="forbid")

    statement: str = Field(min_length=1, max_length=3000)
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Exact opaque Evidence IDs copied from the supplied Specialist "
            "Context only; never observations, excerpts, commands, or log text."
        ),
    )
    contradicting_evidence_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Exact opaque Evidence IDs copied from the supplied Specialist "
            "Context only; never observations, excerpts, commands, or log text."
        ),
    )
