import asyncio

from app.capabilities.investigation.correlation import (
    CorrelatedDiagnosisClaim,
    DiagnosisCertainty,
    DiagnosisConflict,
    FinalDiagnosis,
)
from app.capabilities.investigation.final_diagnosis_synthesizer import (
    FinalDiagnosisNarrativeOutput,
    FinalDiagnosisSynthesizer,
)


def diagnosis(
    *,
    with_conflict=False,
):
    claim = CorrelatedDiagnosisClaim(
        claim_id="inv-1:claim:1",
        title="NGINX service presence",
        description="NGINX appears absent.",
        certainty=(
            DiagnosisCertainty.UNKNOWN
            if with_conflict
            else DiagnosisCertainty.CONFIRMED
        ),
        confidence=0.95,
        specialist_slugs=(
            "nginx",
            "systemd-service",
        ),
        evidence_ids=("e1",),
    )

    conflicts = ()

    if with_conflict:
        conflicts = (
            DiagnosisConflict(
                conflict_id=(
                    "inv-1:conflict:1"
                ),
                title=(
                    "NGINX service presence"
                ),
                diagnostic_states=(
                    "absent",
                    "present",
                ),
                specialist_slugs=(
                    "nginx",
                    "systemd-service",
                ),
                evidence_ids=(
                    "e1",
                    "e2",
                ),
                source_finding_ids=(
                    "f1",
                    "f2",
                ),
                description=(
                    "Explicit state conflict."
                ),
            ),
        )

    return FinalDiagnosis(
        investigation_id="inv-1",
        summary=(
            "One validated diagnosis."
        ),
        claims=(claim,),
        conflicts=conflicts,
        confirmed_count=(
            0
            if with_conflict
            else 1
        ),
        probable_count=0,
        unknown_count=(
            1
            if with_conflict
            else 0
        ),
        conflict_count=(
            len(conflicts)
        ),
        evidence_ids=("e1",),
        specialist_slugs=(
            "nginx",
            "systemd-service",
        ),
        metadata={},
    )


class Client:
    provider_name = "test"
    model_name = "test-model"

    def __init__(self, output):
        self.output = output
        self.calls = []

    async def synthesize(
        self,
        *,
        system_prompt,
        user_prompt,
    ):
        self.calls.append(
            (system_prompt, user_prompt)
        )

        if isinstance(
            self.output,
            Exception,
        ):
            raise self.output

        return self.output


def test_valid_llm_narrative_is_used():
    client = Client(
        FinalDiagnosisNarrativeOutput(
            summary=(
                "NGINX is not present."
            ),
            claim_ids=(
                ["inv-1:claim:1"]
            ),
            conflict_ids=[],
            operator_notes=[
                "Confirm package state."
            ],
        )
    )

    output = asyncio.run(
        FinalDiagnosisSynthesizer(
            client=client
        ).synthesize(
            diagnosis()
        )
    )

    assert output.used_fallback is False
    assert output.claim_ids == (
        "inv-1:claim:1",
    )
    assert output.provider_name == "test"


def test_unknown_claim_id_uses_fallback():
    client = Client(
        FinalDiagnosisNarrativeOutput(
            summary="Invented claim.",
            claim_ids=[
                "invented-claim"
            ],
            conflict_ids=[],
            operator_notes=[],
        )
    )

    output = asyncio.run(
        FinalDiagnosisSynthesizer(
            client=client
        ).synthesize(
            diagnosis()
        )
    )

    assert output.used_fallback is True
    assert output.claim_ids == (
        "inv-1:claim:1",
    )
    assert (
        "unknown claim IDs"
        in output.metadata[
            "fallback_reason"
        ]
    )


def test_conflict_must_be_preserved():
    client = Client(
        FinalDiagnosisNarrativeOutput(
            summary=(
                "A conflict exists."
            ),
            claim_ids=[
                "inv-1:claim:1"
            ],
            conflict_ids=[],
            operator_notes=[],
        )
    )

    output = asyncio.run(
        FinalDiagnosisSynthesizer(
            client=client
        ).synthesize(
            diagnosis(
                with_conflict=True
            )
        )
    )

    assert output.used_fallback is True
    assert output.conflict_ids == (
        "inv-1:conflict:1",
    )


def test_client_failure_uses_deterministic_summary():
    client = Client(
        RuntimeError(
            "provider unavailable"
        )
    )

    expected = diagnosis()

    output = asyncio.run(
        FinalDiagnosisSynthesizer(
            client=client
        ).synthesize(
            expected
        )
    )

    assert output.used_fallback is True
    assert output.summary == (
        expected.summary
    )


def test_no_client_uses_fallback():
    expected = diagnosis(
        with_conflict=True
    )

    output = asyncio.run(
        FinalDiagnosisSynthesizer()
        .synthesize(expected)
    )

    assert output.used_fallback is True
    assert output.provider_name == (
        "deterministic"
    )
    assert output.conflict_ids == (
        "inv-1:conflict:1",
    )


def test_prompt_contains_only_validated_envelope():
    client = Client(
        FinalDiagnosisNarrativeOutput(
            summary="Summary.",
            claim_ids=[
                "inv-1:claim:1"
            ],
            conflict_ids=[],
            operator_notes=[],
        )
    )

    asyncio.run(
        FinalDiagnosisSynthesizer(
            client=client
        ).synthesize(
            diagnosis()
        )
    )

    system_prompt, user_prompt = (
        client.calls[0]
    )

    assert (
        "must not create new claims"
        in system_prompt
    )
    assert (
        '"claim_id":"inv-1:claim:1"'
        in user_prompt
    )
    assert '"certainty":"confirmed"' in (
        user_prompt
    )
