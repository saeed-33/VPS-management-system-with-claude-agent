"""منطق طلب وتحقق مخرج تفكير المتخصص."""
from __future__ import annotations

import logging

import httpx
from pydantic import ValidationError

from app.core.contracts.specialist_reasoning.specialist_final_synthesis_output import SpecialistFinalSynthesisOutput
from app.core.contracts.specialist_reasoning.specialist_reasoning_output import SpecialistReasoningOutput

logger = logging.getLogger(__name__)


class _OllamaReasoningMixin:
    """ينظم طلب التفكير والتحقق من المخرج المنظم."""

    async def reason(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> SpecialistReasoningOutput:
        """
        يرسل سياق المتخصص إلى Ollama، يعيد المحاولة عند مخرج ناقص، ويتحقق من الأدلة وطلبات الأدوات.
        """
        schema = SpecialistReasoningOutput.model_json_schema()

        compact_contract = (
            '{"summary":"brief conclusion","confidence":0.0,'
            '"findings":[{"title":"brief title",'
            '"description":"brief evidence-based description",'
            '"confidence":0.0,"evidence_ids":[],'
            '"knowledge_source_ids":[]}],'
            '"hypotheses":[{"statement":"brief hypothesis",'
            '"confidence":0.0,"supporting_evidence_ids":[],'
            '"contradicting_evidence_ids":[]}],'
            '"ruled_out":[],"missing_evidence":[],'
            '"recommended_next_specialists":[],'
            '"diagnostic_tool_requests":[{"tool_id":"tool-id",'
            '"arguments":{},"rationale":"brief rationale"}],'
            '"recommended_remediation_actions":[{"action_type":"start_service",'
            '"target":"service","reason":"evidence-based reason",'
            '"expected_effect":"service becomes active"}]}'
        )

        is_final_synthesis = (
            "## Final Synthesis Required"
            in user_prompt
        )

        if is_final_synthesis:
            compact_contract = (
                '{"summary":"short conclusion",'
                '"confidence":0.0,'
                '"missing_evidence":[],'
                '"recommended_next_specialists":[]}'
            )

        base_prompt = (
            user_prompt
            + "\n\n## Structured Output Contract\n"
            + "Return exactly one JSON object with this shape:\n"
            + compact_contract
            + (
                "\n\nJSON rules:"
                "\n- Return JSON only; never Markdown fences."
                "\n- Keep summary under 800 characters."
                "\n- Use at most 4 findings and 3 hypotheses."
                "\n- Keep each finding description under 500 characters."
                "\n- Use at most 5 missing_evidence items."
                "\n- Use only exact Evidence IDs and Knowledge Source IDs "
                "from the supplied context."
                "\n- Evidence-ID fields contain only the exact opaque ID "
                "token after `evidence_id:`; never put observations, "
                "excerpts, command output, status text, or log text there."
                "\n- If an Evidence ID is not explicitly supplied, use "
                "an empty Evidence-ID list; never invent or paraphrase one."
                "\n- diagnostic_tool_requests must contain only the minimum "
                "needed Tools."
                "\n- Remediation actions must use action_type, target, reason, "
                "and expected_effect; never use action as the field name."
                "\n- Hypotheses may contain only supporting_evidence_ids and "
                "contradicting_evidence_ids for references; never add "
                "knowledge_source_ids to a hypothesis."
                "\n- Do not restate the supplied context."
                "\n- Do not repeat command output inside prose."
            )
            + (
                (
                    "\n\n## Provider Final-Synthesis Compact Mode"
                    "\nReturn exactly the minimal Final Synthesis object."
                    "\nAllowed keys are only: summary, confidence, "
                    "missing_evidence, recommended_next_specialists."
                    "\nDo not output findings, hypotheses, ruled_out, "
                    "knowledge_source_ids, or diagnostic_tool_requests."
                )
                if is_final_synthesis
                else ""
            )
        )

        use_schema_format = (
            False
            if is_final_synthesis
            else (
                self._schema_format_supported
                is not False
            )
        )
        schema_rejection: str | None = None
        last_error: Exception | None = None
        last_content = ""
        last_done_reason = None
        generation_attempt = 0

        while generation_attempt < 2:
            request_format = (
                schema
                if use_schema_format
                else "json"
            )

            retry_suffix = ""
            if generation_attempt > 0:
                retry_suffix = (
                    "\n\n## Retry Requirement\n"
                    "The previous response was invalid or incomplete. "
                    "Return a much shorter complete JSON object now. "
                    "Do not explain. Do not repeat evidence text. "
                    "Close every quote, bracket, and brace. "
                    "Prefer fewer findings over a truncated response."
                    + (
                        " For Final Synthesis return only summary, "
                        "confidence, missing_evidence, and "
                        "recommended_next_specialists. Do not output findings, "
                        "hypotheses, ruled_out, knowledge_source_ids, or "
                        "diagnostic_tool_requests."
                        if is_final_synthesis
                        else ""
                    )
                )

            response = await self._client.post(
                "/api/chat",
                json={
                    "model": self._model,
                    "stream": False,
                    "think": False,
                    "keep_alive": "15m",
                    "format": request_format,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": (
                                base_prompt
                                + retry_suffix
                            ),
                        },
                    ],
                    "options": {
                        "temperature": 0,
                        "num_ctx": 32768,
                        "num_predict": (
                            6144
                            if generation_attempt == 0
                            else 8192
                        ),
                    },
                },
            )

            try:
                response.raise_for_status()

            except httpx.HTTPStatusError as exc:
                if (
                    use_schema_format
                    and exc.response.status_code == 400
                ):
                    schema_rejection = (
                        exc.response.text[:2000]
                    )
                    logger.warning(
                        "Ollama rejected specialist JSON schema; "
                        "retrying with generic JSON format | model=%s "
                        "status=%s detail=%s",
                        self._model,
                        exc.response.status_code,
                        schema_rejection,
                    )
                    self._schema_format_supported = False
                    use_schema_format = False
                    continue

                detail = (
                    exc.response.text[:2000]
                    if exc.response is not None
                    else ""
                )

                raise RuntimeError(
                    "Ollama specialist request failed "
                    f"with HTTP {exc.response.status_code}: {detail}"
                ) from exc

            if use_schema_format:
                self._schema_format_supported = True

            body = response.json()
            last_done_reason = body.get("done_reason")

            message = body.get("message")
            if not isinstance(message, dict):
                raise RuntimeError(
                    "Ollama specialist response has no valid message."
                )

            content = message.get("content")
            if not isinstance(content, str):
                raise RuntimeError(
                    "Ollama specialist response has no text content."
                )

            last_content = content
            cleaned = content.strip()

            if cleaned.startswith("```"):
                lines = cleaned.splitlines()
                if (
                    lines
                    and lines[0].strip().lower()
                    in {"```json", "```"}
                ):
                    lines = lines[1:]
                if (
                    lines
                    and lines[-1].strip() == "```"
                ):
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()

            try:
                cleaned = self._normalize_compatibility_aliases(cleaned)
                if is_final_synthesis:
                    final_output = (
                        SpecialistFinalSynthesisOutput
                        .model_validate_json(cleaned)
                    )
                    return final_output.to_reasoning_output()

                return (
                    SpecialistReasoningOutput
                    .model_validate_json(cleaned)
                )

            except ValidationError as exc:
                last_error = exc
                generation_attempt += 1
                use_schema_format = False

        compatibility = (
            (
                " Schema format was rejected by the Ollama server: "
                + schema_rejection
            )
            if schema_rejection
            else ""
        )

        raise RuntimeError(
            "Ollama returned invalid specialist structured output "
            "after 2 generated attempts "
            f"(done_reason={last_done_reason!r})."
            + compatibility
            + " Last content: "
            + last_content[:2000]
        ) from last_error
