from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from app.core.contracts.investigation import (
    InvestigationBudget,
    SpecialistTask,
)
from app.bootstrap import container


async def run(args) -> int:
    loop = (
        container
        .specialist_investigation_loop
    )

    if loop is None:
        raise SystemExit(
            "Specialist investigation loop "
            "is unavailable because LLM is disabled."
        )

    specialist = (
        container
        .specialist_registry
        .get_by_slug(
            args.specialist
        )
    )

    if specialist is None:
        raise SystemExit(
            "Enabled Specialist not found: "
            f"{args.specialist}"
        )

    domains = tuple(
        value.strip().casefold()
        for value
        in (args.domains or "").split(",")
        if value.strip()
    )

    task_id = (
        "loop-preview-"
        + uuid4().hex[:12]
    )

    task = SpecialistTask(
        task_id=task_id,
        investigation_id=(
            "loop-preview"
        ),
        server_id=args.server_id,
        report_id=args.report_id,
        specialist_id=specialist.slug,
        objective=args.objective,
        knowledge_topics=(
            specialist.knowledge_topics
        ),
    )

    enabled_slugs = tuple(
        item.slug
        for item
        in container
        .specialist_registry
        .get_enabled()
    )

    result = await loop.run(
        task=task,
        specialist=specialist,
        investigation_budget=(
            InvestigationBudget(
                max_specialists=4,
                max_rounds=(
                    args.max_rounds
                ),
                max_actions=(
                    args.max_actions
                ),
            )
        ),
        detected_domains=domains,
        allowed_specialist_slugs=(
            enabled_slugs
        ),
    )

    print()
    print(
        "# Specialist Investigation Loop"
    )
    print()
    print(
        f"Task:             {task_id}"
    )
    print(
        f"Server:           {args.server_id}"
    )
    print(
        f"Specialist:       {specialist.slug}"
    )
    print(
        f"Provider/model:   "
        f"{result.provider}/{result.model}"
    )
    print(
        f"Stop reason:      "
        f"{result.stop_reason.value}"
    )
    print(
        f"Rounds:           "
        f"{result.rounds_completed}"
    )
    print(
        f"Actions executed: "
        f"{result.actions_executed}"
    )
    print(
        f"Evidence items:   "
        f"{len(result.evidence)}"
    )

    for trace in result.traces:
        print()
        print(
            f"## ROUND "
            f"{trace.round_number}"
        )
        print(
            f"Confidence: "
            f"{trace.confidence:.2f}"
        )
        print(
            "Requested:  "
            + (
                ", ".join(
                    trace.requested_tools
                )
                or "—"
            )
        )
        print(
            "Evidence:   "
            + (
                ", ".join(
                    trace.collected_evidence_ids
                )
                or "—"
            )
        )

        for item in (
            trace.tool_decisions
        ):
            print(
                "- "
                f"{item.tool_id}: "
                f"{item.decision} "
                f"[{', '.join(item.reasons)}]"
            )

    final = result.final_result

    print()
    print(
        "## FINAL SPECIALIST RESULT"
    )
    print()
    print(
        f"Confidence: "
        f"{final.confidence:.2f}"
    )
    print(
        f"Summary: {final.summary}"
    )

    if final.findings:
        print()
        print("### Findings")

        for item in final.findings:
            print(
                f"- {item.title} "
                f"({item.confidence:.2f})"
            )
            print(
                "  evidence="
                + (
                    ", ".join(
                        item.evidence_ids
                    )
                    or "—"
                )
            )

    if final.missing_evidence:
        print()
        print("### Missing Evidence")

        for item in (
            final.missing_evidence
        ):
            print(
                f"- {item}"
            )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "server_id",
        type=int,
    )
    parser.add_argument(
        "specialist",
    )
    parser.add_argument(
        "objective",
    )
    parser.add_argument(
        "--report-id",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--domains",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--max-actions",
        type=int,
        default=12,
    )

    args = parser.parse_args()

    return asyncio.run(
        run(args)
    )


if __name__ == "__main__":
    raise SystemExit(main())
