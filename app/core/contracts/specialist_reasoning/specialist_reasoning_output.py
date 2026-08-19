"""Contract class extracted from specialist_reasoning.py during the structure refactor."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .specialist_diagnostic_tool_request_output import SpecialistDiagnosticToolRequestOutput

from .specialist_finding_output import SpecialistFindingOutput

from .specialist_hypothesis_output import SpecialistHypothesisOutput

from .specialist_remediation_action_output import SpecialistRemediationActionOutput

class SpecialistReasoningOutput(BaseModel):
    """
    النتيجة الكاملة لجولة تفكير متخصص.

    تجمع الملخص والنتائج والفرضيات وما تم استبعاده والأدلة الناقصة وطلبات
    الفحص اللاحقة في شكل واحد قابل للحفظ والمراجعة.
    """
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
    recommended_remediation_actions: list[
        SpecialistRemediationActionOutput
    ] = Field(
        default_factory=list,
        description=(
            "Named, non-shell remediation proposals grounded in the supplied "
            "evidence. These are proposals only and are never executed here."
        ),
    )
