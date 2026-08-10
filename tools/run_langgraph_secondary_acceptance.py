from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.investigation.contracts import InvestigationBudget
from app.agent.investigation.investigation_router import (
    InvestigationRoutingDecision,
    SpecialistRoutingMatch,
)
from app.bootstrap import container


def normalize_issues(value) -> tuple[dict, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return ()
    if isinstance(value, dict):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(
            item
            for item in value
            if isinstance(item, dict)
        )
    return ()


def controlled_initial_decision(
    slug: str,
) -> InvestigationRoutingDecision:
    snapshot = container.specialist_registry.snapshot()
    specialist = snapshot.get_by_slug(slug)

    if specialist is None:
        available = ", ".join(
            sorted(
                item.slug
                for item in snapshot.definitions
            )
        )
        raise SystemExit(
            f"Specialist {slug!r} is unavailable. "
            f"Enabled: {available or '—'}"
        )

    match = SpecialistRoutingMatch(
        specialist_id=specialist.id,
        specialist_slug=specialist.slug,
        specialist_name=specialist.name,
        score=1,
        matched_domains=tuple(
            specialist.domains
        ),
        matched_trigger_hints=(),
        matched_issue_indexes=(),
        priority=specialist.priority,
    )

    return InvestigationRoutingDecision(
        should_investigate=True,
        reasons=(),
        detected_domains=tuple(
            specialist.domains
        ),
        candidate_specialists=(match,),
        selected_specialists=(match,),
        unmatched_issue_indexes=(),
        registry_size=len(
            snapshot.definitions
        ),
        candidate_limit=1,
        selection_limit=1,
    )


async def run(args) -> int:
    coordinator = (
        container
        .dynamic_secondary_coordinator
    )

    if coordinator is None:
        raise SystemExit(
            "Dynamic secondary coordinator "
            "is unavailable. Verify Phase "
            "4.17 bootstrap wiring."
        )

    report = (
        container
        .report_query_service
        .get_report(args.report_id)
    )
    analysis = (
        container
        .analysis_repository
        .get_by_report_id(
            args.report_id
        )
    )

    if analysis is None:
        raise SystemExit(
            f"No analysis for report "
            f"{args.report_id}."
        )

    decision = controlled_initial_decision(
        args.initial_specialist
    )

    print()
    print(
        "# Phase 4.17 Dynamic Secondary "
        "Routing Acceptance"
    )
    print()
    print(
        f"Report ID:             "
        f"{report.id}"
    )
    print(
        f"Server ID:             "
        f"{report.server_id}"
    )
    print(
        f"Initial Specialist:    "
        f"{args.initial_specialist}"
    )
    print(
        "Initial routing:       "
        "CONTROLLED ACCEPTANCE ONLY"
    )
    print(
        "Secondary routing:     "
        "REAL MODEL RECOMMENDATIONS"
    )

    result = await coordinator.run(
        server_id=report.server_id,
        report_id=report.id,
        analysis_id=analysis.id,
        routing_decision=decision,
        budget=InvestigationBudget(
            max_specialists=(
                args.max_specialists
            ),
            max_rounds=args.max_rounds,
            max_actions=args.max_actions,
        ),
        initial_analysis_summary=(
            getattr(
                analysis,
                "summary",
                None,
            )
        ),
        initial_analysis_issues=(
            normalize_issues(
                getattr(
                    analysis,
                    "issues",
                    None,
                )
            )
        ),
    )

    state = result.state

    print()
    print("## RESULT")
    print()
    print(
        f"Status:               "
        f"{state.status.value}"
    )
    print(
        f"Execution mode:       "
        f"{state.metadata.get('execution_mode')}"
    )
    print(
        f"Waves completed:      "
        f"{state.metadata.get('waves_completed')}"
    )
    print(
        f"Actions used:         "
        f"{result.investigation_actions_used}"
        f"/{state.budget.max_actions}"
    )
    print(
        "Executed Specialists: "
        + ", ".join(
            state.metadata.get(
                "executed_specialists",
                [],
            )
        )
    )
    print(
        "Secondary requested:  "
        + (
            ", ".join(
                state.metadata.get(
                    "secondary_requested",
                    [],
                )
            )
            or "—"
        )
    )
    print(
        "Secondary accepted:   "
        + (
            ", ".join(
                state.metadata.get(
                    "secondary_accepted",
                    [],
                )
            )
            or "—"
        )
    )

    for index, item in enumerate(
        result.runs,
        start=1,
    ):
        print()
        print(
            f"## RUN {index}: "
            f"{item.specialist_slug}"
        )
        print()
        print(
            f"Status:      "
            f"{item.result.status.value}"
        )
        print(
            f"Confidence:  "
            f"{item.result.confidence:.2f}"
        )
        print(
            "Recommends:  "
            + (
                ", ".join(
                    item.result
                    .recommended_next_specialists
                )
                or "—"
            )
        )
        print()
        print(
            item.result.summary
        )

    checks = {
        "langgraph_orchestrator": (
            state.metadata.get(
                "orchestrator"
            )
            == "langgraph"
        ),
        "dynamic_secondary_mode": (
            state.metadata.get(
                "execution_mode"
            )
            == "dynamic-secondary"
        ),
        "global_action_budget_safe": (
            result.investigation_actions_used
            <= state.budget.max_actions
        ),
        "specialist_budget_safe": (
            len(
                state.metadata.get(
                    "executed_specialists",
                    [],
                )
            )
            <= state.budget.max_specialists
        ),
        "no_duplicate_specialists": (
            len(
                state.metadata.get(
                    "executed_specialists",
                    [],
                )
            )
            == len(
                set(
                    state.metadata.get(
                        "executed_specialists",
                        [],
                    )
                )
            )
        ),
    }

    if args.require_secondary:
        checks[
            "secondary_specialist_executed"
        ] = bool(
            state.metadata.get(
                "secondary_accepted",
                [],
            )
        )

    print()
    print("## ACCEPTANCE CHECKS")
    print()

    for name, passed in checks.items():
        print(
            f"- {name}: "
            + (
                "PASS"
                if passed
                else "FAIL"
            )
        )

    return (
        0
        if all(checks.values())
        else 2
    )


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "report_id",
        type=int,
    )
    parser.add_argument(
        "--initial-specialist",
        default="nginx",
    )
    parser.add_argument(
        "--max-specialists",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--max-actions",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--require-secondary",
        action="store_true",
    )

    return asyncio.run(
        run(parser.parse_args())
    )


if __name__ == "__main__":
    raise SystemExit(main())
