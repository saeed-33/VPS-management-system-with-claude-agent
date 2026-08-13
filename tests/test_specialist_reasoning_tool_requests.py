import asyncio

from app.domain.investigation.diagnostic_tools import (
    DiagnosticToolCall,
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

    def __init__(self):
        self.user_prompt = None

    async def reason(
        self,
        *,
        system_prompt,
        user_prompt,
    ):
        self.user_prompt = user_prompt

        return SpecialistReasoningOutput(
            summary="Need live status.",
            confidence=0.2,
            diagnostic_tool_requests=[
                {
                    "tool_id": "systemd-status",
                    "arguments": {
                        "service": "nginx",
                    },
                    "rationale": (
                        "Need current service state."
                    ),
                }
            ],
        )


def context():
    return SpecialistContextSnapshot(
        task_id="task-1",
        investigation_id="inv-1",
        specialist_slug="nginx",
        specialist_name="Nginx Investigator",
        objective="Investigate.",
        instructions=None,
        domains=("nginx",),
        knowledge_query="test",
        initial_analysis_summary=None,
        initial_analysis_issues=(),
        evidence=(),
        incidents=(),
        knowledge_chunks=(),
        knowledge_sources=(),
        rendered_context="base context",
        character_count=12,
    )


def test_reasoning_returns_structured_tool_requests():
    client = Client()

    execution = asyncio.run(
        SpecialistReasoningAgent(
            client=client
        ).reason(
            context=context(),
            diagnostic_tool_catalog=(
                '[{"tool_id":"systemd-status"}]'
            ),
        )
    )

    assert len(
        execution.diagnostic_tool_requests
    ) == 1

    request = (
        execution
        .diagnostic_tool_requests[0]
    )

    assert isinstance(
        request.call,
        DiagnosticToolCall,
    )
    assert request.call.tool_id == (
        "systemd-status"
    )
    assert request.call.arguments == {
        "service": "nginx",
    }
    assert (
        request.rationale
        == "Need current service state."
    )

    assert (
        "Available Diagnostic Tools"
        in client.user_prompt
    )
