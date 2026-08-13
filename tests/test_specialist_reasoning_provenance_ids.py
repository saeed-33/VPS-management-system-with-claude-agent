import asyncio

from app.domain.investigation.contracts import (
    EvidenceKind,
    EvidenceReference,
)
from app.domain.investigation.specialist_context import (
    SpecialistContextSnapshot,
)
from app.domain.investigation.specialist_reasoning_agent import (
    SpecialistReasoningAgent,
)
from app.core.contracts.specialist_reasoning import (
    SpecialistReasoningOutput,
)


class Client:
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self, output):
        self.output = output

    async def reason(self, *, system_prompt, user_prompt):
        return self.output


def context():
    evidence = EvidenceReference(
        evidence_id="analysis:638:issue:1",
        kind=EvidenceKind.ANALYSIS,
        title="Connection failure",
        source_id=638,
        excerpt="Connect call failed.",
    )

    return SpecialistContextSnapshot(
        task_id="task-1",
        investigation_id="inv-1",
        specialist_slug="linux-network",
        specialist_name="Linux Network",
        objective="Investigate connectivity.",
        instructions=None,
        domains=("network",),
        knowledge_query="test",
        initial_analysis_summary=None,
        initial_analysis_issues=(),
        evidence=(evidence,),
        incidents=(),
        knowledge_chunks=(),
        knowledge_sources=(),
        rendered_context=(
            "[evidence]\n"
            "evidence_id: analysis:638:issue:1\n"
            "excerpt: Connect call failed."
        ),
        character_count=100,
    )


def test_evidence_namespace_prefix_is_normalized_only_for_real_id():
    output = SpecialistReasoningOutput(
        summary="Connection evidence exists.",
        confidence=0.8,
        findings=[
            {
                "title": "Connection failed",
                "description": "SSH connection failed.",
                "confidence": 0.9,
                "evidence_ids": [
                    "evidence:analysis:638:issue:1"
                ],
                "knowledge_source_ids": [],
            }
        ],
    )

    execution = asyncio.run(
        SpecialistReasoningAgent(
            client=Client(output)
        ).reason(
            context=context(),
        )
    )

    assert execution.result.findings[0].evidence_ids == (
        "analysis:638:issue:1",
    )


def test_unknown_prefixed_reference_remains_rejected():
    output = SpecialistReasoningOutput(
        summary="Bad citation.",
        confidence=0.2,
        findings=[
            {
                "title": "Bad",
                "description": "Bad citation.",
                "confidence": 0.2,
                "evidence_ids": [
                    "evidence:not-a-real-id"
                ],
                "knowledge_source_ids": [],
            }
        ],
    )

    try:
        asyncio.run(
            SpecialistReasoningAgent(
                client=Client(output)
            ).reason(
                context=context(),
            )
        )
    except ValueError as exc:
        assert "unknown evidence IDs" in str(exc)
    else:
        raise AssertionError(
            "Unknown reference should fail closed."
        )
