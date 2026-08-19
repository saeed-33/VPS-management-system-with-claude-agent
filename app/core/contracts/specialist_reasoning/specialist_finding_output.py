"""Contract class extracted from specialist_reasoning.py during the structure refactor."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

class SpecialistFindingOutput(BaseModel):
    """
    نتيجة يزعم المتخصص أنها مدعومة بأدلة محددة.
    """
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=4000)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Exact opaque Evidence IDs copied from the supplied Specialist "
            "Context only; never observations, excerpts, commands, or log text."
        ),
    )
    knowledge_source_ids: list[str] = Field(default_factory=list)
