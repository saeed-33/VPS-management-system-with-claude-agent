"""
عميل Ollama يترجم contracts الداخلية إلى HTTP model calls ويعيد DTOs.

الموقع في المعمارية: LLM infrastructure.
يُستدعى بواسطة: capabilities عبر protocol/client factory.
يعتمد مباشرة على: app.core.contracts.final_diagnosis.
الحد المعماري: Ollama مزود model فقط؛ لا يمنح النص صلاحية policy أو persistence.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

import httpx

from app.core.contracts.final_diagnosis import (
    FinalDiagnosisNarrativeClient,
    FinalDiagnosisNarrativeOutput,
)

class OllamaFinalDiagnosisNarrativeClient(
    FinalDiagnosisNarrativeClient
):
    """
    يمثل OllamaFinalDiagnosisNarrativeClient مسؤولية محددة داخل طبقة LLM infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities عبر protocol/client factory
    ويعتمد على FinalDiagnosisNarrativeClient وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة LLM infrastructure.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: base_url، model، timeout_seconds.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._model = model
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(
                connect=10.0,
                read=timeout_seconds,
                write=30.0,
                pool=10.0,
            ),
        )

    @property
    def provider_name(self) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة LLM infrastructure.

        تُستدعى عندما يصل workflow إلى provider_name؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return "ollama"

    @property
    def model_name(self) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة LLM infrastructure.

        تُستدعى عندما يصل workflow إلى model_name؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._model

    async def synthesize(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> FinalDiagnosisNarrativeOutput:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة LLM infrastructure.

        تُستدعى عندما يصل workflow إلى synthesize؛ المدخلات المهمة: system_prompt، user_prompt.
        تعيد FinalDiagnosisNarrativeOutput أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        contract = (
            '{"summary":"brief server-level diagnosis",'
            '"claim_ids":[],"conflict_ids":[],'
            '"operator_notes":[]}'
        )

        response = await self._client.post(
            "/api/chat",
            json={
                "model": self._model,
                "stream": False,
                "think": False,
                "keep_alive": "15m",
                "format": "json",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": (
                            user_prompt
                            + "\n\nReturn exactly this JSON shape:\n"
                            + contract
                        ),
                    },
                ],
                "options": {
                    "temperature": 0,
                    "num_ctx": 32768,
                    "num_predict": 4096,
                },
            },
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = (
                exc.response.text[:2000]
                if exc.response is not None
                else ""
            )
            raise RuntimeError(
                "Ollama final diagnosis request failed "
                f"with HTTP {exc.response.status_code}: {detail}"
            ) from exc

        body = response.json()
        message = body.get("message")

        if not isinstance(message, dict):
            raise RuntimeError(
                "Ollama final diagnosis response "
                "has no valid message."
            )

        content = message.get("content")

        if not isinstance(content, str):
            raise RuntimeError(
                "Ollama final diagnosis response "
                "has no text content."
            )

        return (
            FinalDiagnosisNarrativeOutput
            .model_validate_json(
                content.strip()
            )
        )

    async def close(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة LLM infrastructure.

        تُستدعى عندما يصل workflow إلى close؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        await self._client.aclose()

__all__ = [
    'OllamaFinalDiagnosisNarrativeClient',
]
