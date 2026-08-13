from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.composition import container


def print_matches(title, matches):
    print()
    print(title)
    print("-" * 96)
    print(f"{'SPECIALIST':24} {'SCORE':6} {'PRIORITY':8} MATCH")

    for item in matches:
        parts = []
        if item.matched_trigger_hints:
            parts.append(
                "triggers=" + "|".join(item.matched_trigger_hints)
            )
        if item.matched_domains:
            parts.append(
                "domains=" + "|".join(item.matched_domains)
            )

        print(
            f"{item.specialist_slug:24} "
            f"{item.score:<6} "
            f"{item.priority:<8} "
            + "; ".join(parts)
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report_id", type=int)
    args = parser.parse_args()

    report = container.report_query_service.get_report(args.report_id)
    analysis = container.analysis_repository.get_by_report_id(args.report_id)

    if analysis is None:
        raise SystemExit(
            f"No analysis exists for report_id={args.report_id}."
        )

    decision = container.investigation_router.route(
        report=report,
        analysis=analysis,
    )

    print()
    print("Investigation Routing Decision")
    print("=" * 96)
    print(f"Report ID:           {args.report_id}")
    print(f"Should investigate:  {decision.should_investigate}")
    print(
        "Reasons:             "
        + ", ".join(x.value for x in decision.reasons)
    )
    print(
        "Detected domains:    "
        + (", ".join(decision.detected_domains) or "—")
    )
    print(f"Registry size:       {decision.registry_size}")
    print(f"Candidate limit:     {decision.candidate_limit}")
    print(f"Selection limit:     {decision.selection_limit}")

    print_matches(
        "CANDIDATE SPECIALISTS",
        decision.candidate_specialists,
    )
    print_matches(
        "BASELINE SELECTED SPECIALISTS",
        decision.selected_specialists,
    )

    print()
    print(
        f"Candidate specialists: {len(decision.candidate_specialists)}"
    )
    print(
        f"Selected specialists:  {len(decision.selected_specialists)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
