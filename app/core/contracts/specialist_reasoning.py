"""
عقود وDTOs مشتركة لنقل البيانات بين الطبقات.

الموقع في المعمارية: Core application contracts.
يُستدعى بواسطة: capabilities وinterfaces وadapters.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا تنفذ I/O أو workflow.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SpecialistReasoningClient(ABC):
    """
    يمثل SpecialistReasoningClient مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على ABC وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

        تُستدعى عندما يصل workflow إلى provider_name؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

        تُستدعى عندما يصل workflow إلى model_name؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        raise NotImplementedError

    @abstractmethod
    async def reason(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> "SpecialistReasoningOutput":
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

        تُستدعى عندما يصل workflow إلى reason؛ المدخلات المهمة: system_prompt، user_prompt.
        تعيد 'SpecialistReasoningOutput' أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        raise NotImplementedError


class SpecialistFindingOutput(BaseModel):
    """
    يمثل SpecialistFindingOutput مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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


class SpecialistHypothesisOutput(BaseModel):
    """
    يمثل SpecialistHypothesisOutput مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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


class SpecialistDiagnosticToolRequestOutput(BaseModel):
    """
    يمثل SpecialistDiagnosticToolRequestOutput مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    model_config = ConfigDict(extra="forbid")

    tool_id: str = Field(min_length=1, max_length=120)
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(min_length=1, max_length=1000)


class SpecialistReasoningOutput(BaseModel):
    """
    يمثل SpecialistReasoningOutput مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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

class SpecialistFinalSynthesisOutput(BaseModel):
    """
    يمثل SpecialistFinalSynthesisOutput مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

        تُستدعى عندما يصل workflow إلى to_reasoning_output؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد SpecialistReasoningOutput أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        )
