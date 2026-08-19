"""Contract class extracted from specialist_reasoning.py during the structure refactor."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .specialist_reasoning_output import SpecialistReasoningOutput

class SpecialistFinalSynthesisOutput(BaseModel):
    """
    ملخص نهائي للمتخصص عند بلوغ حد الجولات أو الأفعال.
    """
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=5000)
    confidence: float = Field(ge=0.0, le=1.0)
    missing_evidence: list[str] = Field(default_factory=list)
    recommended_next_specialists: list[str] = Field(
        default_factory=list
    )

    def to_reasoning_output(self) -> SpecialistReasoningOutput:
        """
        يحول الملخص النهائي إلى نتيجة جولة لا تحتوي طلبات أدوات جديدة.

        تستخدمه الحلقة لإغلاق التحقيق بقراءة الأدلة المتاحة بدل فتح جولة بعد
        نفاد الميزانية.
        """
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
            recommended_remediation_actions=[],
        )
