from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
import json

import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, Field

from app.domain.investigation.correlation import (
    FinalDiagnosis,
)
from app.shared.config import Settings


class FinalDiagnosisNarrativeOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(
        min_length=1,
        max_length=2000,
    )
    claim_ids: list[str] = Field(
        default_factory=list
    )
    conflict_ids: list[str] = Field(
        default_factory=list
    )
    operator_notes: list[str] = Field(
        default_factory=list,
        max_length=5,
    )


@dataclass(slots=True, frozen=True)
class FinalDiagnosisNarrative:
    summary: str
    claim_ids: tuple[str, ...]
    conflict_ids: tuple[str, ...]
    operator_notes: tuple[str, ...]
    provider_name: str
    model_name: str
    used_fallback: bool
    metadata: dict


class FinalDiagnosisNarrativeClient(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def synthesize(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> FinalDiagnosisNarrativeOutput:
        raise NotImplementedError


class OllamaFinalDiagnosisNarrativeClient(
    FinalDiagnosisNarrativeClient
):
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
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
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    async def synthesize(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> FinalDiagnosisNarrativeOutput:
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
        await self._client.aclose()


class OpenAIFinalDiagnosisNarrativeClient(
    FinalDiagnosisNarrativeClient
):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        if not api_key.strip():
            raise ValueError(
                "OPENAI_API_KEY is required when "
                "LLM_PROVIDER=openai."
            )

        self._model = model
        self._timeout_seconds = (
            timeout_seconds
        )
        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
        )

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    async def synthesize(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> FinalDiagnosisNarrativeOutput:
        response = await asyncio.wait_for(
            self._client.responses.parse(
                model=self._model,
                input=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                text_format=(
                    FinalDiagnosisNarrativeOutput
                ),
            ),
            timeout=self._timeout_seconds,
        )

        if response.output_parsed is None:
            raise RuntimeError(
                "OpenAI returned no parsed "
                "final diagnosis narrative."
            )

        return response.output_parsed


class FinalDiagnosisSynthesizer:
    SYSTEM_PROMPT = """
You write a concise server-level diagnostic narrative.

The supplied claims and conflicts are already validated by deterministic
correlation. You must not create new claims, change certainty labels, infer
new Evidence IDs, or resolve conflicts yourself.

You may only:
- summarize the validated diagnosis;
- order existing claim IDs by diagnostic importance;
- order existing conflict IDs by diagnostic importance;
- provide up to five short operator notes.

Every claim_id and conflict_id you return must be copied exactly from the
input. If a conflict exists, describe it as unresolved. Do not downgrade or
upgrade confirmed/probable/unknown labels.
""".strip()

    def __init__(
        self,
        *,
        client: (
            FinalDiagnosisNarrativeClient
            | None
        ) = None,
    ) -> None:
        self._client = client

    async def synthesize(
        self,
        diagnosis: FinalDiagnosis,
    ) -> FinalDiagnosisNarrative:
        if self._client is None:
            return self._fallback(
                diagnosis,
                reason="client_unavailable",
            )

        prompt = self._render_prompt(
            diagnosis
        )

        try:
            output = await (
                self._client.synthesize(
                    system_prompt=(
                        self.SYSTEM_PROMPT
                    ),
                    user_prompt=prompt,
                )
            )

            self._validate_output(
                diagnosis=diagnosis,
                output=output,
            )

            return FinalDiagnosisNarrative(
                summary=output.summary,
                claim_ids=tuple(
                    output.claim_ids
                ),
                conflict_ids=tuple(
                    output.conflict_ids
                ),
                operator_notes=tuple(
                    output.operator_notes
                ),
                provider_name=(
                    self._client.provider_name
                ),
                model_name=(
                    self._client.model_name
                ),
                used_fallback=False,
                metadata={
                    "synthesizer": (
                        "llm-assisted"
                    ),
                    "validated_claim_count": (
                        len(diagnosis.claims)
                    ),
                    "validated_conflict_count": (
                        len(
                            diagnosis.conflicts
                        )
                    ),
                },
            )

        except Exception as exc:
            return self._fallback(
                diagnosis,
                reason=(
                    f"{type(exc).__name__}: "
                    f"{str(exc)[:500]}"
                ),
            )

    def _validate_output(
        self,
        *,
        diagnosis: FinalDiagnosis,
        output: FinalDiagnosisNarrativeOutput,
    ) -> None:
        allowed_claims = {
            claim.claim_id
            for claim in diagnosis.claims
        }
        allowed_conflicts = {
            conflict.conflict_id
            for conflict
            in diagnosis.conflicts
        }

        unknown_claims = [
            claim_id
            for claim_id
            in output.claim_ids
            if claim_id
            not in allowed_claims
        ]

        if unknown_claims:
            raise ValueError(
                "Final diagnosis narrative "
                "referenced unknown claim IDs: "
                + ", ".join(
                    unknown_claims
                )
            )

        unknown_conflicts = [
            conflict_id
            for conflict_id
            in output.conflict_ids
            if conflict_id
            not in allowed_conflicts
        ]

        if unknown_conflicts:
            raise ValueError(
                "Final diagnosis narrative "
                "referenced unknown conflict IDs: "
                + ", ".join(
                    unknown_conflicts
                )
            )

        if (
            diagnosis.conflicts
            and not output.conflict_ids
        ):
            raise ValueError(
                "Final diagnosis narrative "
                "omitted unresolved conflicts."
            )

    def _render_prompt(
        self,
        diagnosis: FinalDiagnosis,
    ) -> str:
        payload = {
            "investigation_id": (
                diagnosis.investigation_id
            ),
            "deterministic_summary": (
                diagnosis.summary
            ),
            "counts": {
                "confirmed": (
                    diagnosis.confirmed_count
                ),
                "probable": (
                    diagnosis.probable_count
                ),
                "unknown": (
                    diagnosis.unknown_count
                ),
                "conflicts": (
                    diagnosis.conflict_count
                ),
            },
            "claims": [
                {
                    "claim_id": (
                        claim.claim_id
                    ),
                    "title": claim.title,
                    "description": (
                        claim.description
                    ),
                    "certainty": (
                        claim.certainty.value
                    ),
                    "confidence": (
                        claim.confidence
                    ),
                    "specialists": list(
                        claim.specialist_slugs
                    ),
                    "evidence_ids": list(
                        claim.evidence_ids
                    ),
                    "missing_evidence": list(
                        claim.missing_evidence
                    ),
                }
                for claim in diagnosis.claims
            ],
            "conflicts": [
                {
                    "conflict_id": (
                        conflict.conflict_id
                    ),
                    "title": conflict.title,
                    "diagnostic_states": list(
                        conflict
                        .diagnostic_states
                    ),
                    "specialists": list(
                        conflict
                        .specialist_slugs
                    ),
                    "evidence_ids": list(
                        conflict.evidence_ids
                    ),
                    "description": (
                        conflict.description
                    ),
                }
                for conflict
                in diagnosis.conflicts
            ],
        }

        return (
            "Validated diagnosis input:\n"
            + json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )

    def _fallback(
        self,
        diagnosis: FinalDiagnosis,
        *,
        reason: str,
    ) -> FinalDiagnosisNarrative:
        notes = []

        if diagnosis.conflicts:
            notes.append(
                "Unresolved cross-Specialist "
                "conflicts require operator review."
            )

        if diagnosis.unknown_count:
            notes.append(
                f"{diagnosis.unknown_count} "
                "claim(s) remain unknown."
            )

        if diagnosis.probable_count:
            notes.append(
                f"{diagnosis.probable_count} "
                "claim(s) remain probable."
            )

        return FinalDiagnosisNarrative(
            summary=diagnosis.summary,
            claim_ids=tuple(
                claim.claim_id
                for claim
                in diagnosis.claims
            ),
            conflict_ids=tuple(
                conflict.conflict_id
                for conflict
                in diagnosis.conflicts
            ),
            operator_notes=tuple(
                notes[:5]
            ),
            provider_name=(
                self._client.provider_name
                if self._client is not None
                else "deterministic"
            ),
            model_name=(
                self._client.model_name
                if self._client is not None
                else "none"
            ),
            used_fallback=True,
            metadata={
                "synthesizer": (
                    "deterministic-fallback"
                ),
                "fallback_reason": reason,
                "validated_claim_count": (
                    len(diagnosis.claims)
                ),
                "validated_conflict_count": (
                    len(diagnosis.conflicts)
                ),
            },
        )


def create_final_diagnosis_narrative_client(
    settings: Settings,
) -> FinalDiagnosisNarrativeClient:
    if not settings.llm_enabled:
        raise RuntimeError(
            "LLM analysis is disabled."
        )

    if settings.llm_provider == "ollama":
        return (
            OllamaFinalDiagnosisNarrativeClient(
                base_url=(
                    settings.ollama_base_url
                ),
                model=settings.ollama_model,
                timeout_seconds=(
                    settings
                    .llm_analysis_timeout_seconds
                ),
            )
        )

    if settings.llm_provider == "openai":
        return (
            OpenAIFinalDiagnosisNarrativeClient(
                api_key=(
                    settings.openai_api_key
                    or ""
                ),
                model=settings.openai_model,
                timeout_seconds=(
                    settings
                    .llm_analysis_timeout_seconds
                ),
            )
        )

    raise ValueError(
        "Unsupported LLM provider: "
        f"{settings.llm_provider}"
    )
