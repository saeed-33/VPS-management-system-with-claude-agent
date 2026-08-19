"""Contract class extracted from specialist_reasoning.py during the structure refactor."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any, Literal

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
