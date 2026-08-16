"""عقود مخرجات تفكير المتخصص وطلبات فحوصه الإضافية."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SpecialistReasoningClient(ABC):
    """
    عقد لمزود يحلل سياق متخصص ويرجع نتائج مرتبطة بمعرفات أدلة معروفة.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """يعيد اسم مزود التفكير لتسجيل مصدر نتيجة المتخصص."""
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """يعيد اسم النموذج الذي أنتج نتيجة المتخصص."""
        raise NotImplementedError

    @abstractmethod
    async def reason(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> "SpecialistReasoningOutput":
        """
        يحلل سياق المتخصص ويرجع نتائج وفرضيات أو طلب أداة تشخيص مسموحة.
        """
        raise NotImplementedError


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


class SpecialistDiagnosticToolRequestOutput(BaseModel):
    """
    طلب فحص إضافي يشرح المتخصص سبب حاجته إليه.

    لا يمثل الطلب إذنًا بالتنفيذ؛ تمر الأداة لاحقًا عبر سياسة التحقيق والتحقق
    من المعاملات قبل جمع دليل جديد.
    """
    model_config = ConfigDict(extra="forbid")

    tool_id: str = Field(min_length=1, max_length=120)
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(min_length=1, max_length=1000)


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
        )
