from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SpecialistReasoningClient(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def reason(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> "SpecialistReasoningOutput":
        raise NotImplementedError


class SpecialistFindingOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=4000)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)
    knowledge_source_ids: list[str] = Field(default_factory=list)


class SpecialistHypothesisOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    statement: str = Field(min_length=1, max_length=3000)
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)


class SpecialistDiagnosticToolRequestOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_id: str = Field(min_length=1, max_length=120)
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(min_length=1, max_length=1000)


class SpecialistReasoningOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=5000)
    confidence: float = Field(ge=0.0, le=1.0)
    findings: list[SpecialistFindingOutput] = Field(default_factory=list)
    hypotheses: list[SpecialistHypothesisOutput] = Field(default_factory=list)
    ruled_out: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    recommended_next_specialists: list[str] = Field(default_factory=list)
    diagnostic_tool_requests: list[
        SpecialistDiagnosticToolRequestOutput
    ] = Field(default_factory=list)

class SpecialistFinalSynthesisOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=5000)
    confidence: float = Field(ge=0.0, le=1.0)
    missing_evidence: list[str] = Field(default_factory=list)
    recommended_next_specialists: list[str] = Field(
        default_factory=list
    )

    def to_reasoning_output(self) -> SpecialistReasoningOutput:
        return SpecialistReasoningOutput(
            summary=self.summary,
            confidence=self.confidence,
            findings=[],
            hypotheses=[],
            ruled_out=[],
            missing_evidence=list(self.missing_evidence),
            recommended_next_specialists=list(
                self.recommended_next_specialists
            ),
            diagnostic_tool_requests=[],
        )
