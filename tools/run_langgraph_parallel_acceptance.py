from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.investigation.contracts import InvestigationBudget
from app.agent.investigation.investigation_router import (
    InvestigationRoutingDecision,
    RoutingReason,
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
        return tuple(x for x in value if isinstance(x, dict))
    return ()


def controlled_decision(slugs: tuple[str, ...]) -> InvestigationRoutingDecision:
    snapshot = container.specialist_registry.snapshot()
    by_slug = {item.slug: item for item in snapshot.definitions}

    missing = tuple(slug for slug in slugs if slug not in by_slug)
    if missing:
        available = ", ".join(sorted(by_slug)) or "—"
        raise SystemExit(
            "Controlled acceptance specialists are unavailable/enabled: "
            + ", ".join(missing)
            + "\nAvailable enabled specialists: "
            + available
        )

    matches = []
    detected_domains = set()

    for slug in slugs:
        specialist = by_slug[slug]
        domains = tuple(specialist.domains)
        detected_domains.update(domains)

        matches.append(
            SpecialistRoutingMatch(
                specialist_id=specialist.id,
                specialist_slug=specialist.slug,
                specialist_name=specialist.name,
                score=1,
                matched_domains=domains,
                matched_trigger_hints=(),
                matched_issue_indexes=(),
                priority=specialist.priority,
            )
        )

    selected = tuple(matches)
    return InvestigationRoutingDecision(
        should_investigate=True,
        reasons=(RoutingReason.ANALYSIS_ISSUES,),
        detected_domains=tuple(sorted(detected_domains)),
        candidate_specialists=selected,
        selected_specialists=selected,
        unmatched_issue_indexes=(),
        registry_size=len(snapshot.definitions),
        candidate_limit=max(len(selected), 1),
        selection_limit=max(len(selected), 1),
    )


async def run(args) -> int:
    coordinator = container.langgraph_server_coordinator
    if coordinator is None:
        raise SystemExit(
            "LangGraph Server Coordinator is unavailable. "
            "Verify Phase 4.16 bootstrap wiring."
        )

    report = container.report_query_service.get_report(args.report_id)
    analysis = container.analysis_repository.get_by_report_id(args.report_id)
    if analysis is None:
        raise SystemExit(f"No analysis exists for report_id={args.report_id}.")

    slugs = tuple(
        part.strip()
        for part in args.specialists.split(",")
        if part.strip()
    )
    if len(slugs) < 2:
        raise SystemExit(
            "This acceptance requires at least two comma-separated specialists."
        )
    if len(set(slugs)) != len(slugs):
        raise SystemExit("Specialist slugs must be unique.")

    decision = controlled_decision(slugs)

    print()
    print("# Phase 4.16 Controlled Parallel Runtime Acceptance")
    print()
    print(f"Report ID:             {report.id}")
    print(f"Server ID:             {report.server_id}")
    print(f"Analysis ID:           {analysis.id}")
    print("Routing source:        CONTROLLED ACCEPTANCE ONLY")
    print("Selected Specialists:  " + ", ".join(decision.selected_slugs))
    print("Production router used: NO")
    print("Real LangGraph runtime: YES")
    print("Real Specialist loops: YES")
    print("Real Policy/SSH/tools:  YES")

    started = time.perf_counter()
    result = await coordinator.run(
        server_id=report.server_id,
        report_id=report.id,
        analysis_id=analysis.id,
        routing_decision=decision,
        budget=InvestigationBudget(
            max_specialists=max(args.max_specialists, len(slugs)),
            max_rounds=args.max_rounds,
            max_actions=args.max_actions,
        ),
        initial_analysis_summary=getattr(analysis, "summary", None),
        initial_analysis_issues=normalize_issues(
            getattr(analysis, "issues", None)
        ),
    )
    elapsed = time.perf_counter() - started
    state = result.state

    print()
    print("## GRAPH RESULT")
    print()
    print(f"Investigation ID:      {state.investigation_id}")
    print(f"Status:                {state.status.value}")
    print(f"Orchestrator:          {state.metadata.get('orchestrator')}")
    print(f"Execution mode:        {state.metadata.get('execution_mode')}")
    print(f"Specialist runs:       {len(result.runs)}")
    print(
        f"Actions used:          {result.investigation_actions_used}"
        f"/{state.budget.max_actions}"
    )
    print(
        "Quota total:           "
        f"{state.metadata.get('parallel_action_quota_total')}"
    )
    print(f"Evidence items:        {len(state.evidence)}")
    print(f"Wall time:             {elapsed:.2f}s")

    quotas = []
    worker_actions = 0

    for index, item in enumerate(result.runs, start=1):
        quota = int(item.task.metadata.get("parallel_action_quota", 0) or 0)
        quotas.append(quota)

        actions = 0
        rounds = 0
        stop_reason = "—"
        if item.loop_result is not None:
            actions = item.loop_result.actions_executed
            rounds = item.loop_result.rounds_completed
            stop_reason = item.loop_result.stop_reason.value
        worker_actions += actions

        print()
        print(f"## WORKER {index}: {item.specialist_slug}")
        print()
        print(f"Status:      {item.result.status.value}")
        print(f"Quota:       {quota}")
        print(f"Confidence:  {item.result.confidence:.2f}")
        print(f"Rounds:      {rounds}")
        print(f"Actions:     {actions}")
        print(f"Stop reason: {stop_reason}")
        print()
        print(item.result.summary)

        if item.result.status.value == "failed":
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
                    item.result.metadata.get(
                        "error"
                    )
                    or "—"
                )
            )
            print(
                "- Metadata: "
                + repr(item.result.metadata)
            )

    actual_slugs = tuple(item.specialist_slug for item in result.runs)

    checks = {
        "two_or_more_workers": len(result.runs) >= 2,
        "requested_workers_preserved": actual_slugs == slugs,
        "langgraph_orchestrator": (
            state.metadata.get("orchestrator") == "langgraph"
        ),
        "parallel_mode": (
            state.metadata.get("execution_mode") == "parallel"
        ),
        "global_budget_safe": (
            result.investigation_actions_used <= state.budget.max_actions
        ),
        "worker_action_sum_safe": worker_actions <= state.budget.max_actions,
        "quota_budget_safe": sum(quotas) <= state.budget.max_actions,
        "each_worker_within_quota": all(
            (
                item.loop_result is None
                or item.loop_result.actions_executed
                <= int(item.task.metadata.get("parallel_action_quota", 0) or 0)
            )
            for item in result.runs
        ),
    }

    print()
    print("## ACCEPTANCE CHECKS")
    print()
    for name, passed in checks.items():
        print(f"- {name}: {'PASS' if passed else 'FAIL'}")

    print()
    print(
        "NOTE: This tool intentionally overrides only the initial routing "
        "decision. It does not modify the database or production routing."
    )

    return 0 if all(checks.values()) else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Controlled Phase 4.16 runtime acceptance for real "
            "multi-Specialist LangGraph fan-out."
        )
    )
    parser.add_argument("report_id", type=int)
    parser.add_argument(
        "--specialists",
        default="linux-cpu,linux-memory",
        help="Comma-separated enabled Specialist slugs.",
    )
    parser.add_argument("--max-specialists", type=int, default=2)
    parser.add_argument("--max-rounds", type=int, default=2)
    parser.add_argument("--max-actions", type=int, default=8)
    return asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
