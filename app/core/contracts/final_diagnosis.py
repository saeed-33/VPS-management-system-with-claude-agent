"""عقود صياغة التشخيص النهائي من نتائج المتخصصين والأدلة المتعارضة."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field


class FinalDiagnosisNarrativeOutput(BaseModel):
    """
    النص المنظم الذي يعيده مزود صياغة التشخيص النهائي.

    يقتصر على ملخص ومعرفات الادعاءات والتعارضات وملاحظات المشغل، ولا يسمح
    بإضافة دليل أو إجراء غير موجود في حالة التحقيق.
    """
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=2000)
    claim_ids: list[str] = Field(default_factory=list)
    conflict_ids: list[str] = Field(default_factory=list)
    operator_notes: list[str] = Field(default_factory=list, max_length=5)


@dataclass(slots=True, frozen=True)
class FinalDiagnosisNarrative:
    """
    صياغة تشخيص نهائي محفوظة مع مصدر النموذج وبيان استخدام fallback.
    """
    summary: str
    claim_ids: tuple[str, ...]
    conflict_ids: tuple[str, ...]
    operator_notes: tuple[str, ...]
    provider_name: str
    model_name: str
    used_fallback: bool
    metadata: dict


class FinalDiagnosisNarrativeClient(ABC):
    """
    عقد لمزود يحول نتائج التحقيق إلى سرد تشخيصي قابل للعرض.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """يعيد اسم مزود صياغة التشخيص المستخدم للتتبع والمراجعة."""
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """يعيد اسم النموذج الذي صاغ السرد النهائي."""
        raise NotImplementedError

    @abstractmethod
    async def synthesize(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> FinalDiagnosisNarrativeOutput:
        """
        يصوغ ملخصًا نهائيًا من سياق التحقيق المقدم دون إنشاء ادعاءات جديدة.
        """
        raise NotImplementedError
