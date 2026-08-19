"""عميل HTTP لجلسات تفكير Ollama."""
from __future__ import annotations

import httpx

from app.core.contracts.specialist_reasoning.specialist_reasoning_client import SpecialistReasoningClient

from .compatibility import normalize_compatibility_aliases
from .reasoning import _OllamaReasoningMixin


class OllamaSpecialistReasoningClient(_OllamaReasoningMixin, SpecialistReasoningClient):
    """عميل يشغل تفكير المتخصص ويقبل مخرجًا منظمًا."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        """
        يهيئ عميل تفكير المتخصص ويحتفظ بقدرة المزود على قبول مخطط JSON.
        """
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(
                connect=10.0,
                read=timeout_seconds,
                write=30.0,
                pool=10.0,
            ),
        )

        self._schema_format_supported: bool | None = None

    @property
    def provider_name(self) -> str:
        """
        يعيد اسم مزود تفكير المتخصص.
        """
        return "ollama"

    @property
    def model_name(self) -> str:
        """
        يعيد اسم النموذج الذي يفسر سياق المتخصص.
        """
        return self._model

    async def close(self) -> None:
        """
        يغلق عميل HTTP الخاص بجلسات تفكير المتخصص.
        """
        await self._client.aclose()

    @staticmethod
    def _normalize_compatibility_aliases(content: str) -> str:
        """يطبق تطبيع التوافق قبل التحقق من العقد."""
        return normalize_compatibility_aliases(content)
