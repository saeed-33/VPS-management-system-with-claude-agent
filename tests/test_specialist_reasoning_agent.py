import asyncio

import pytest

from app.agent.investigation.contracts import (
    KnowledgeSourceReference,
    KnowledgeSourceType,
)
from app.agent.investigation.specialist_context import (
    SpecialistContextSnapshot,
)
from app.agent.investigation.specialist_reasoning_agent import (
    SpecialistReasoningAgent,
)
from app.shared.dto.specialist_reasoning import (
    SpecialistFindingOutput,
    SpecialistHypothesisOutput,
    SpecialistReasoningOutput,
)


class Client:
    provider_name = "test"
    model_name = "test-model"

    def __init__(self, output):
        self.output = output
        self.system_prompt = None
        self.user_prompt = None

    async def reason(self, *, system_prompt, user_prompt):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        return self.output


def context():
    return SpecialistContextSnapshot(
        task_id="task-1",
        investigation_id="inv-1",
        specialist_slug="nginx",
        specialist_name="NGINX Specialist",
        objective="Diagnose 502 errors.",
        instructions="Use supplied evidence only.",
        domains=("nginx", "proxy"),
        knowledge_query="nginx proxy 502",
        initial_analysis_summary=None,
        initial_analysis_issues=(),
        evidence=(),
        incidents=(),
        knowledge_chunks=(),
        knowledge_sources=(
            KnowledgeSourceReference(
                source_id="knowledge-chunk:12",
                source_type=(
                    KnowledgeSourceType.OFFICIAL_DOCUMENTATION
                ),
                title="NGINX docs",
            ),
        ),
        rendered_context=(
            "[knowledge:chunk-12] proxy documentation"
        ),
        character_count=46,
    )


def valid_output():
    return SpecialistReasoningOutput(
        summary="The current context suggests a proxy-related path.",
        confidence=0.55,
        findings=[
            SpecialistFindingOutput(
                title="Proxy module is relevant",
                description=(
                    "The supplied documentation identifies proxy support."
                ),
                confidence=0.7,
                knowledge_source_ids=["knowledge-chunk:12"],
            )
        ],
        hypotheses=[
            SpecialistHypothesisOutput(
                statement=(
                    "The 502 may originate from an unavailable upstream."
                ),
                confidence=0.45,
            )
        ],
        missing_evidence=[
            "NGINX error log around the failing request."
        ],
        recommended_next_specialists=[],
    )


def test_reasoning_converts_valid_output_to_contract():
    client = Client(valid_output())
    agent = SpecialistReasoningAgent(client=client)

    execution = asyncio.run(
        agent.reason(context=context())
    )

    result = execution.result

    assert result.status.value == "completed"
    assert result.findings[0].knowledge_source_ids == (
        "knowledge-chunk:12",
    )
    assert result.missing_evidence == (
        "NGINX error log around the failing request.",
    )
    assert result.metadata["reasoning_only"] is True


def test_unknown_knowledge_citation_is_rejected():
    output = valid_output()
    output.findings[0].knowledge_source_ids = [
        "knowledge-chunk:999"
    ]

    agent = SpecialistReasoningAgent(
        client=Client(output)
    )

    with pytest.raises(
        ValueError,
        match="unknown knowledge IDs",
    ):
        asyncio.run(
            agent.reason(context=context())
        )


def test_unknown_recommended_specialist_is_dropped():
    output = valid_output()
    output.recommended_next_specialists = [
        "invented-specialist"
    ]

    agent = SpecialistReasoningAgent(
        client=Client(output)
    )

    execution = asyncio.run(
        agent.reason(
            context=context(),
            allowed_specialist_slugs=(
                "nginx",
                "linux-network",
            ),
        )
    )

    assert execution.result.recommended_next_specialists == ()
    assert execution.result.metadata[
        "dropped_specialist_recommendations"
    ] == ["invented-specialist"]


def test_systemd_alias_maps_to_systemd_service():
    output = valid_output()
    output.recommended_next_specialists = [
        "systemd",
        "logging",
    ]

    agent = SpecialistReasoningAgent(
        client=Client(output)
    )

    execution = asyncio.run(
        agent.reason(
            context=context(),
            allowed_specialist_slugs=(
                "nginx",
                "systemd-service",
                "linux-network",
            ),
        )
    )

    assert execution.result.recommended_next_specialists == (
        "systemd-service",
    )
    assert execution.result.metadata[
        "dropped_specialist_recommendations"
    ] == ["logging"]


def test_prompt_has_no_tool_execution_request():
    client = Client(valid_output())
    agent = SpecialistReasoningAgent(client=client)

    asyncio.run(
        agent.reason(context=context())
    )

    assert "read-only" in client.system_prompt
    assert "performed any external action" in client.system_prompt
