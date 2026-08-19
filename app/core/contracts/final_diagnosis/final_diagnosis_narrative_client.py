"""Contract class extracted from final_diagnosis.py during the structure refactor."""

from __future__ import annotations

from abc import ABC, abstractmethod

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

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
