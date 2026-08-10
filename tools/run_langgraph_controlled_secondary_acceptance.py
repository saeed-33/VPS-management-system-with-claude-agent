from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.investigation.contracts import (
    InvestigationBudget,
    SpecialistTaskStatus,
)
from app.agent.investigation.investigation_router import (
    InvestigationRoutingDecision,
    SpecialistRoutingMatch,
)
from app.agent.investigation.langgraph_secondary_orchestrator import (
    DynamicSecondaryLangGraphCoordinator,
)
from app.bootstrap import container


class ControlledRecommendationParallelCoordinator:
    """Acceptance-only adapter around the real Phase 4.16 coordinator."""

    def __init__(self, *, delegate, secondary_slug: str) -> None:
        self._delegate = delegate
        self._secondary_slug = secondary_slug
        self._first_wave_seen = False
        self.recommendation_injected = False

    async def run(self, **kwargs):
        result = await self._delegate.run(**kwargs)

        if self._first_wave_seen:
            return result

        self._first_wave_seen = True

        if not result.runs:
            return result

        first = result.runs[0]

        if first.result.status != SpecialistTaskStatus.COMPLETED:
            return result

        metadata = dict(first.result.metadata)
        metadata.update(
            {
                "acceptance_controlled_recommendation": True,
                "acceptance_secondary_slug": self._secondary_slug,
            }
        )

        controlled_result = replace(
            first.result,
            recommended_next_specialists=(self._secondary_slug,),
            metadata=metadata,
        )
        controlled_run = replace(
            first,
            result=controlled_result,
        )

        self.recommendation_injected = True

        return replace(
            result,
            runs=(controlled_run, *result.runs[1:]),
        )


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
            item for item in value
            if isinstance(item, dict)
        )
    return ()


def specialist_by_slug(slug: str):
    snapshot = container.specialist_registry.snapshot()
    specialist = snapshot.get_by_slug(slug)

    if specialist is None:
        available = ", ".join(
            sorted(item.slug for item in snapshot.definitions)
        )
        raise SystemExit(
            f"Specialist {slug!r} is unavailable/enabled. "
            f"Enabled: {available or '—'}"
        )

    return specialist, snapshot


def controlled_initial_decision(
    slug: str,
) -> InvestigationRoutingDecision:
    specialist, snapshot = specialist_by_slug(slug)

    match = SpecialistRoutingMatch(
        specialist_id=specialist.id,
        specialist_slug=specialist.slug,
        specialist_name=specialist.name,
        score=1,
        matched_domains=tuple(specialist.domains),
        matched_trigger_hints=(),
        matched_issue_indexes=(),
        priority=specialist.priority,
    )

    return InvestigationRoutingDecision(
        should_investigate=True,
        reasons=(),
        detected_domains=tuple(specialist.domains),
        candidate_specialists=(match,),
        selected_specialists=(match,),
        unmatched_issue_indexes=(),
        registry_size=len(snapshot.definitions),
        candidate_limit=1,
        selection_limit=1,
    )


async def run(args) -> int:
    if args.initial_specialist == args.secondary_specialist:
        raise SystemExit(
            "Initial and secondary Specialists must be different."
        )

    specialist_by_slug(args.secondary_specialist)

    parallel = container.langgraph_server_coordinator
    if parallel is None:
        raise SystemExit(
            "Phase 4.16 LangGraph coordinator is unavailable."
        )

    adapter = ControlledRecommendationParallelCoordinator(
        delegate=parallel,
        secondary_slug=args.secondary_specialist,
    )

    coordinator = DynamicSecondaryLangGraphCoordinator(
        specialist_registry=container.specialist_registry,
        parallel_coordinator=adapter,
    )

    report = container.report_query_service.get_report(args.report_id)
    analysis = container.analysis_repository.get_by_report_id(
        args.report_id
    )

    if analysis is None:
        raise SystemExit(
            f"No analysis exists for report_id={args.report_id}."
        )

    decision = controlled_initial_decision(
        args.initial_specialist
    )

    print()
    print("# Phase 4.17 Controlled Secondary Runtime Acceptance")
    print()
    print(f"Report ID:                {report.id}")
    print(f"Server ID:                {report.server_id}")
    print(f"Initial Specialist:       {args.initial_specialist}")
    print(f"Controlled Secondary:     {args.secondary_specialist}")
    print("Initial routing:          CONTROLLED ACCEPTANCE")
    print("Primary execution:        REAL")
    print(
        "Recommendation source:    "
        "CONTROLLED AFTER PRIMARY SUCCESS"
    )
    print(
        "Secondary validation:     "
        "REAL 4.17 REGISTRY/BUDGET LOGIC"
    )
    print("Secondary execution:      REAL")
    print("Production code changed:  NO")
    print("Database changed:         NO")

    result = await coordinator.run(
        server_id=report.server_id,
        report_id=report.id,
        analysis_id=analysis.id,
        routing_decision=decision,
        budget=InvestigationBudget(
            max_specialists=2,
            max_rounds=args.max_rounds,
            max_actions=args.max_actions,
        ),
        initial_analysis_summary=getattr(
            analysis,
            "summary",
            None,
        ),
        initial_analysis_issues=normalize_issues(
            getattr(
                analysis,
                "issues",
                None,
            )
        ),
    )

    state = result.state
    executed = tuple(
        state.metadata.get("executed_specialists", [])
    )
    requested = tuple(
        state.metadata.get("secondary_requested", [])
    )
    accepted = tuple(
        state.metadata.get("secondary_accepted", [])
    )

    print()
    print("## RESULT")
    print()
    print(f"Status:                  {state.status.value}")
    print(
        f"Execution mode:          "
        f"{state.metadata.get('execution_mode')}"
    )
    print(
        f"Waves completed:         "
        f"{state.metadata.get('waves_completed')}"
    )
    print(
        f"Actions used:            "
        f"{result.investigation_actions_used}"
        f"/{state.budget.max_actions}"
    )
    print(
        "Executed Specialists:    "
        + (", ".join(executed) or "—")
    )
    print(
        "Secondary requested:     "
        + (", ".join(requested) or "—")
    )
    print(
        "Secondary accepted:      "
        + (", ".join(accepted) or "—")
    )

    for index, item in enumerate(result.runs, start=1):
        print()
        print(f"## RUN {index}: {item.specialist_slug}")
        print()
        print(f"Status:      {item.result.status.value}")
        print(f"Confidence:  {item.result.confidence:.2f}")
        print(
            "Recommends:  "
            + (
                ", ".join(
                    item.result.recommended_next_specialists
                )
                or "—"
            )
        )

        if item.loop_result is not None:
            print(
                f"Rounds:      "
                f"{item.loop_result.rounds_completed}"
            )
            print(
                f"Actions:     "
                f"{item.loop_result.actions_executed}"
            )
            print(
                f"Stop reason: "
                f"{item.loop_result.stop_reason.value}"
            )

        print()
        print(item.result.summary)

        if item.result.status == SpecialistTaskStatus.FAILED:
            print()
            print("Failure diagnostics:")
            print(
                "- Type:  "
                + str(
                    item.result.metadata.get(
                        "coordinator_failure"
                    )
                    or "—"
                )
            )
            print(
                "- Error: "
                + str(
                    item.result.metadata.get("error")
                    or "—"
                )
            )

    run_by_slug = {
        item.specialist_slug: item
        for item in result.runs
    }
    primary_run = run_by_slug.get(
        args.initial_specialist
    )
    secondary_run = run_by_slug.get(
        args.secondary_specialist
    )

    checks = {
        "primary_completed": (
            primary_run is not None
            and primary_run.result.status
            == SpecialistTaskStatus.COMPLETED
        ),
        "controlled_recommendation_injected": (
            adapter.recommendation_injected
        ),
        "two_waves_completed": (
            state.metadata.get("waves_completed", 0) >= 2
        ),
        "secondary_requested": (
            args.secondary_specialist in requested
        ),
        "secondary_accepted_by_real_4_17": (
            args.secondary_specialist in accepted
        ),
        "secondary_executed": (
            args.secondary_specialist in executed
        ),
        "secondary_completed": (
            secondary_run is not None
            and secondary_run.result.status
            == SpecialistTaskStatus.COMPLETED
        ),
        "global_action_budget_safe": (
            result.investigation_actions_used
            <= state.budget.max_actions
        ),
        "specialist_budget_safe": (
            len(executed)
            <= state.budget.max_specialists
        ),
        "no_duplicate_specialists": (
            len(executed) == len(set(executed))
        ),
    }

    print()
    print("## ACCEPTANCE CHECKS")
    print()

    for name, passed in checks.items():
        print(
            f"- {name}: "
            + ("PASS" if passed else "FAIL")
        )

    print()
    print(
        "NOTE: Only the recommendation value is controlled. "
        "Both Specialist executions and all 4.17 validation/routing "
        "after the recommendation use the real runtime."
    )

    return 0 if all(checks.values()) else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report_id", type=int)
    parser.add_argument(
        "--initial-specialist",
        default="nginx",
    )
    parser.add_argument(
        "--secondary-specialist",
        default="systemd-service",
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

    return asyncio.run(
        run(parser.parse_args())
    )


if __name__ == "__main__":
    raise SystemExit(main())
