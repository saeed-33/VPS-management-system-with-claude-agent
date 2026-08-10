import asyncio

from app.agent.investigation.specialist_context import (
    SpecialistContextSnapshot,
)
from app.agent.investigation.specialist_reasoning_agent import (
    SpecialistReasoningAgent,
)
from app.shared.dto.specialist_reasoning import (
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
            summary="Need direct NGINX evidence.",
            confidence=0.2,
        )


def context():
    objective = (
        "Determine whether NGINX is installed/running "
        "and what live evidence supports the conclusion."
    )

    return SpecialistContextSnapshot(
        task_id="task-1",
        investigation_id="inv-1",
        specialist_slug="nginx",
        specialist_name="Nginx Investigator",
        objective=objective,
        instructions=None,
        domains=("nginx", "http", "network"),
        knowledge_query="test",
        initial_analysis_summary=None,
        initial_analysis_issues=(),
        evidence=(),
        incidents=(),
        knowledge_chunks=(),
        knowledge_sources=(),
        rendered_context=(
            "## Specialist\n"
            "slug: nginx\n"
            f"objective: {objective}"
        ),
        character_count=100,
    )


def test_objective_is_prominent_before_and_after_catalog():
    client = Client()
    ctx = context()

    asyncio.run(
        SpecialistReasoningAgent(
            client=client
        ).reason(
            context=ctx,
            diagnostic_tool_catalog=(
                '[{"tool_id":"systemd-status"},'
                '{"tool_id":"network-route"}]'
            ),
        )
    )

    prompt = client.user_prompt

    assert prompt.startswith(
        "## Mandatory Investigation Objective\n"
        + ctx.objective
    )

    catalog_index = prompt.index(
        "## Available Diagnostic Tools"
    )

    reminder_index = prompt.index(
        "## Objective Reminder"
    )

    assert reminder_index > catalog_index
    assert (
        ctx.objective
        in prompt[reminder_index:]
    )
    assert (
        "The Tool catalog is capability metadata, "
        "not the problem statement."
        in prompt
    )
