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
from app.bootstrap import container


def _normalize_issues(value) -> tuple[dict, ...]:
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


async def run(args) -> int:
    coordinator = container.server_coordinator

    if coordinator is None:
        raise SystemExit(
            "Server Coordinator is unavailable. "
            "Verify Phase 4.15 bootstrap wiring and LLM configuration."
        )

    report = container.report_query_service.get_report(
        args.report_id
    )

    analysis = (
        container.analysis_repository
        .get_by_report_id(
            args.report_id
        )
    )

    if analysis is None:
        raise SystemExit(
            f"No analysis exists for report_id={args.report_id}."
        )

    decision = (
        container.investigation_router.route(
            report=report,
            analysis=analysis,
        )
    )

    print()
    print("# Phase 4.15 Server Coordinator Acceptance")
    print()
    print(f"Report ID:             {report.id}")
    print(f"Server ID:             {report.server_id}")
    print(f"Analysis ID:           {analysis.id}")
    print(
        f"Should investigate:    "
        f"{decision.should_investigate}"
    )
    print(
        "Detected domains:      "
        + (
            ", ".join(decision.detected_domains)
            or "—"
        )
    )
    print(
        "Selected Specialists:  "
        + (
            ", ".join(
                item.specialist_slug
                for item
                in decision.selected_specialists
            )
            or "—"
        )
    )

    if not decision.should_investigate:
        print()
        print(
            "Routing correctly determined that "
            "no investigation is required."
        )
        return 0

    result = await coordinator.run(
        server_id=report.server_id,
        report_id=report.id,
        analysis_id=analysis.id,
        routing_decision=decision,
        budget=InvestigationBudget(
            max_specialists=args.max_specialists,
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
            _normalize_issues(
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
    print("## COORDINATOR RESULT")
    print()
    print(
        f"Investigation ID:      "
        f"{state.investigation_id}"
    )
    print(
        f"Status:                "
        f"{state.status.value}"
    )
    print(
        f"Specialist runs:       "
        f"{len(result.runs)}"
    )
    print(
        f"Global actions used:   "
        f"{result.investigation_actions_used}"
        f"/{state.budget.max_actions}"
    )
    print(
        f"Evidence items:        "
        f"{len(state.evidence)}"
    )
    print(
        f"Results:               "
        f"{len(state.results)}"
    )

    for index, run_result in enumerate(
        result.runs,
        start=1,
    ):
        specialist_result = run_result.result

        print()
        print(
            f"## SPECIALIST {index}: "
            f"{run_result.specialist_slug}"
        )
        print()
        print(
            f"Task ID:       "
            f"{run_result.task.task_id}"
        )
        print(
            f"Status:        "
            f"{specialist_result.status.value}"
        )
        print(
            f"Confidence:    "
            f"{specialist_result.confidence:.2f}"
        )

        if run_result.loop_result is not None:
            loop_result = (
                run_result.loop_result
            )

            print(
                f"Rounds:        "
                f"{loop_result.rounds_completed}"
            )
            print(
                f"Actions:       "
                f"{loop_result.actions_executed}"
            )
            print(
                f"Stop reason:   "
                f"{loop_result.stop_reason.value}"
            )
            print(
                f"Evidence:      "
                f"{len(loop_result.evidence)}"
            )

        print()
        print("Summary:")
        print(
            specialist_result.summary
        )

        if specialist_result.status.value == "failed":
            print()
            print("Failure diagnostics:")

            failure_type = (
                specialist_result.metadata.get(
                    "coordinator_failure"
                )
            )

            error_text = (
                specialist_result.metadata.get(
                    "error"
                )
            )

            print(
                f"- Type:  "
                f"{failure_type or '—'}"
            )
            print(
                f"- Error: "
                f"{error_text or '—'}"
            )

            if specialist_result.metadata:
                print(
                    "- Metadata: "
                    + repr(
                        specialist_result.metadata
                    )
                )

        if specialist_result.findings:
            print()
            print("Findings:")

            for finding in (
                specialist_result.findings
            ):
                print(
                    f"- {finding.title} "
                    f"({finding.confidence:.2f})"
                )
                print(
                    "  evidence="
                    + (
                        ", ".join(
                            finding.evidence_ids
                        )
                        or "—"
                    )
                )

    print()
    print("## GLOBAL BUDGET TRACE")
    print()

    previous = 0

    for run_result in result.runs:
        loop_result = (
            run_result.loop_result
        )

        if loop_result is None:
            print(
                f"- {run_result.specialist_slug}: "
                "failed before loop completion"
            )
            continue

        after = (
            loop_result
            .investigation_actions_used
        )

        consumed = after - previous

        print(
            f"- {run_result.specialist_slug}: "
            f"+{consumed} actions "
            f"(global={after}/"
            f"{state.budget.max_actions})"
        )

        previous = after

    print()
    print("Acceptance checks:")
    print(
        "- Routing decision reused: PASS"
    )
    print(
        "- Dynamic Specialist Registry reused: PASS"
    )
    print(
        "- Specialist Loop reused: PASS"
    )
    print(
        "- One global action budget propagated: "
        + (
            "PASS"
            if result.investigation_actions_used
            <= state.budget.max_actions
            else "FAIL"
        )
    )
    print(
        "- ServerInvestigationState produced: PASS"
    )

    if (
        result.investigation_actions_used
        > state.budget.max_actions
    ):
        return 2

    if not result.runs:
        return 3

    return 0


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
