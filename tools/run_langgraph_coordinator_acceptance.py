from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

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

from app.agent.investigation.contracts import (
    InvestigationBudget,
)
from app.bootstrap import container


def normalize_issues(
    value,
) -> tuple[dict, ...]:
    if value is None:
        return ()

    if isinstance(value, str):
        try:
            value = json.loads(
                value
            )
        except json.JSONDecodeError:
            return ()

    if isinstance(value, dict):
        return (value,)

    if isinstance(
        value,
        (list, tuple),
    ):
        return tuple(
            item
            for item in value
            if isinstance(
                item,
                dict,
            )
        )

    return ()


async def run(args) -> int:
    coordinator = (
        container
        .langgraph_server_coordinator
    )

    if coordinator is None:
        raise SystemExit(
            "LangGraph Server Coordinator "
            "is unavailable. Verify Phase "
            "4.16 bootstrap wiring and LLM "
            "configuration."
        )

    report = (
        container
        .report_query_service
        .get_report(
            args.report_id
        )
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
            "No analysis exists for "
            f"report_id={args.report_id}."
        )

    decision = (
        container
        .investigation_router
        .route(
            report=report,
            analysis=analysis,
        )
    )

    print()
    print(
        "# Phase 4.16 LangGraph "
        "Parallel Acceptance"
    )
    print()
    print(
        f"Report ID:            "
        f"{report.id}"
    )
    print(
        f"Server ID:            "
        f"{report.server_id}"
    )
    print(
        f"Analysis ID:          "
        f"{analysis.id}"
    )
    print(
        f"Should investigate:   "
        f"{decision.should_investigate}"
    )
    print(
        "Selected Specialists: "
        + (
            ", ".join(
                item.specialist_slug
                for item
                in decision
                .selected_specialists
            )
            or "—"
        )
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
            max_rounds=(
                args.max_rounds
            ),
            max_actions=(
                args.max_actions
            ),
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
    print(
        "## GRAPH RESULT"
    )
    print()
    print(
        f"Investigation ID:     "
        f"{state.investigation_id}"
    )
    print(
        f"Status:               "
        f"{state.status.value}"
    )
    print(
        f"Orchestrator:         "
        f"{state.metadata.get('orchestrator')}"
    )
    print(
        f"Execution mode:       "
        f"{state.metadata.get('execution_mode')}"
    )
    print(
        f"Specialist runs:      "
        f"{len(result.runs)}"
    )
    print(
        f"Actions used:         "
        f"{result.investigation_actions_used}"
        f"/{state.budget.max_actions}"
    )
    print(
        f"Quota total:          "
        f"{state.metadata.get('parallel_action_quota_total')}"
    )
    print(
        f"Evidence items:       "
        f"{len(state.evidence)}"
    )

    for index, item in enumerate(
        result.runs,
        start=1,
    ):
        quota = (
            item.task.metadata.get(
                "parallel_action_quota"
            )
        )

        print()
        print(
            f"## WORKER {index}: "
            f"{item.specialist_slug}"
        )
        print()
        print(
            f"Status:      "
            f"{item.result.status.value}"
        )
        print(
            f"Quota:       "
            f"{quota}"
        )
        print(
            f"Confidence:  "
            f"{item.result.confidence:.2f}"
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
        print(
            item.result.summary
        )

        if (
            item.result.status.value
            == "failed"
        ):
            print()
            print(
                "Failure diagnostics:"
            )
            print(
                "- Type:  "
                + str(
                    item.result.metadata
                    .get(
                        "coordinator_failure"
                    )
                )
            )
            print(
                "- Error: "
                + str(
                    item.result.metadata
                    .get("error")
                )
            )

    checks = {
        "langgraph_orchestrator": (
            state.metadata.get(
                "orchestrator"
            )
            == "langgraph"
        ),
        "parallel_mode": (
            state.metadata.get(
                "execution_mode"
            )
            == "parallel"
        ),
        "global_budget_safe": (
            result
            .investigation_actions_used
            <= state.budget.max_actions
        ),
        "quota_budget_safe": (
            state.metadata.get(
                "parallel_action_quota_total",
                0,
            )
            <= state.budget.max_actions
        ),
    }

    print()
    print(
        "## ACCEPTANCE CHECKS"
    )
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
        "--max-specialists",
        type=int,
        default=4,
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

    return asyncio.run(
        run(
            parser.parse_args()
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
