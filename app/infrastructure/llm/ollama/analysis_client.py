"""
إرسال تقرير المراقبة إلى Ollama وتحويل الرد إلى نتيجة تحليل منظمة.
"""
import json
import logging
from typing import Any

import httpx

from app.capabilities.analysis.llm_client import (
    LLMAnalysisClient,
)
from app.core.contracts.analysis import (
    ReportAnalysisResult,
)

logger = logging.getLogger(__name__)


class OllamaAnalysisClient(LLMAnalysisClient):
    """
    عميل يطلب تحليل تقرير المراقبة من Ollama ويتحقق من JSON والنتيجة قبل إعادتها.
    """
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        """
        يهيئ عميل التحليل بعنوان Ollama والنموذج وحدود القراءة والكتابة.
        """
        if not base_url.strip():
            raise ValueError(
                "OLLAMA_BASE_URL cannot be empty."
            )

        if not model.strip():
            raise ValueError(
                "OLLAMA_MODEL cannot be empty."
            )

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

    @property
    def provider_name(self) -> str:
        """
        يعيد اسم مزود تحليل التقارير.
        """
        return "ollama"

    @property
    def model_name(self) -> str:
        """
        يعيد اسم النموذج الذي يحلل تقرير المراقبة.
        """
        return self._model

    def _extract_json_content(
        self,
        content: str,
    ) -> str:
        """
        يزيل غلاف Markdown من رد Ollama قبل محاولة قراءة JSON التحليل.
        """
        cleaned = content.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines and lines[0].strip().lower() in {
                "```json",
                "```",
            }:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

        return cleaned

    async def analyze_report(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> ReportAnalysisResult:
        """
        يبني عقد JSON من مخطط التحليل، يطلب النتيجة من Ollama، ويعيدها بعد التحقق أو يعيد فشلًا واضحًا.
        """
        schema = (
            ReportAnalysisResult
            .model_json_schema()
        )

        schema_text = json.dumps(
            schema,
            ensure_ascii=False,
            indent=2,
        )

        effective_user_prompt = f"""
{user_prompt}

Return exactly one complete JSON object matching
the following JSON Schema:

{schema_text}

Output requirements:
- Return JSON only.
- Do not include Markdown code fences.
- Do not include text before or after the JSON.
- Include every required property.
- Do not stop before closing the JSON object.
"""

        def make_payload(num_predict: int) -> dict[str, Any]:
            """
            يبني جسم طلب Ollama لمحاولة تحليل واحدة مع عدد مخرجات محدد.
            """
            return {
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
                            effective_user_prompt
                        ),
                    },
                ],
                "options": {
                    "temperature": 0,
                    "num_predict": num_predict,
                },
            }

        last_error: Exception | None = None

        for attempt, num_predict in [(1, 4096), (2, 8192)]:
            payload = make_payload(num_predict)

            try:
                response = await self._client.post(
                    "/api/chat",
                    json=payload,
                )

                response.raise_for_status()

            except httpx.ConnectError as exc:
                raise RuntimeError(
                    "Cannot connect to Ollama at "
                    f"{self._base_url}. Ensure Ollama "
                    "is running."
                ) from exc

            except httpx.ReadTimeout as exc:
                raise RuntimeError(
                    "Ollama analysis exceeded the "
                    f"{self._timeout_seconds}-second timeout. "
                    "Use a smaller model, reduce the report "
                    "size, or increase the timeout."
                ) from exc

            except httpx.HTTPStatusError as exc:
                response_text = (
                    exc.response.text[:2000]
                )

                logger.error(
                    "Ollama analysis request rejected | model=%s "
                    "status=%s detail=%s",
                    self._model,
                    exc.response.status_code,
                    response_text,
                )

                raise RuntimeError(
                    "Ollama returned HTTP "
                    f"{exc.response.status_code}: "
                    f"{response_text}"
                ) from exc

            try:
                body = response.json()
            except ValueError as exc:
                if attempt == 1:
                    last_error = exc
                    continue
                raise RuntimeError(
                    "Ollama returned invalid JSON. "
                    "Response could not be parsed."
                ) from exc

            message = body.get("message")

            if not isinstance(message, dict):
                raise RuntimeError(
                    "Ollama response does not contain "
                    "a valid message."
                )

            content = message.get("content")

            if not isinstance(content, str):
                raise RuntimeError(
                    "Ollama response does not contain "
                    "text content."
                )

            logger.info(
                "Ollama response metadata: done_reason=%s, "
                "prompt_eval_count=%s, eval_count=%s, "
                "content_length=%s, thinking_length=%s",
                body.get("done_reason"),
                body.get("prompt_eval_count"),
                body.get("eval_count"),
                len(content),
                body.get("thinking_length"),
            )

            try:
                json_content = self._extract_json_content(
                    content
                )
                decoded = json.loads(
                    json_content
                )
            except json.JSONDecodeError as exc:
                done_reason = body.get("done_reason")

                if (
                    attempt == 1
                    and done_reason == "length"
                ):
                    last_error = exc
                    continue

                raise RuntimeError(
                    "Ollama returned invalid JSON. "
                    f"done_reason={done_reason!r}. "
                    f"Response: {content[:2000]}"
                ) from exc

            if (
                attempt == 1
                and body.get("done_reason") == "length"
            ):
                last_error = RuntimeError(
                    "Ollama response truncated due to length. "
                    "Retrying with a larger output limit."
                )
                continue

            return ReportAnalysisResult.model_validate(
                decoded
            )

        raise RuntimeError(
            "Ollama analysis failed after retrying with "
            "a larger output limit."
        ) from last_error

    async def health_check(self) -> None:
        """
        يتحقق من وصول Ollama ومن تثبيت النموذج المطلوب قبل بدء التحليل.
        """
        try:
            response = await self._client.get(
                "/api/tags"
            )

            response.raise_for_status()

        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Ollama is not reachable at "
                f"{self._base_url}."
            ) from exc

        body = response.json()
        models = body.get("models", [])

        available_model_names = {
            model.get("name")
            for model in models
            if isinstance(model, dict)
        }

        if self._model not in available_model_names:
            raise RuntimeError(
                f"Ollama model '{self._model}' "
                "is not installed. Available models: "
                f"{sorted(available_model_names)}"
            )

    async def close(self) -> None:
        """
        يغلق عميل HTTP الخاص بطلبات التحليل ويحرر الاتصال.
        """
        await self._client.aclose()
