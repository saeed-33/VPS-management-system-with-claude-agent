from __future__ import annotations

import json

from app.capabilities.investigation.correlation import (
    FinalDiagnosis,
)
from app.core.config import Settings
from app.core.contracts.final_diagnosis import (
    FinalDiagnosisNarrative,
    FinalDiagnosisNarrativeClient,
    FinalDiagnosisNarrativeOutput,
)





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
    from app.infrastructure.llm.ollama.final_diagnosis_client import (
        OllamaFinalDiagnosisNarrativeClient,
    )
    if not settings.llm_enabled:
        raise RuntimeError(
            "LLM analysis is disabled."
        )

    if settings.llm_provider != "ollama":
        raise ValueError(
            "Only LLM_PROVIDER=ollama is supported."
        )

    return OllamaFinalDiagnosisNarrativeClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=(
            settings.llm_analysis_timeout_seconds
        ),
    )

def __getattr__(name: str):
    if name == 'OllamaFinalDiagnosisNarrativeClient':
        from app.infrastructure.llm.ollama.final_diagnosis_client import (
            OllamaFinalDiagnosisNarrativeClient,
        )
        return OllamaFinalDiagnosisNarrativeClient

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )
