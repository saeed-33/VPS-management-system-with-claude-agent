from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.bootstrap import container


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect the Phase 4.5 routing decision "
            "for an existing analyzed monitoring report."
        )
    )

    parser.add_argument(
        "report_id",
        type=int,
    )

    args = parser.parse_args()

    report = (
        container.report_query_service
        .get_report(args.report_id)
    )

    analysis = (
        container.analysis_repository
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
        container.investigation_router
        .route(
            report=report,
            analysis=analysis,
        )
    )

    print()
    print("Investigation Routing Decision")
    print("=" * 96)

    print(
        f"Report ID:           "
        f"{args.report_id}"
    )
    print(
        f"Should investigate:  "
        f"{decision.should_investigate}"
    )
    print(
        "Reasons:             "
        + ", ".join(
            reason.value
            for reason in decision.reasons
        )
    )
    print(
        "Detected domains:    "
        + (
            ", ".join(
                decision.detected_domains
            )
            or "—"
        )
    )
    print(
        f"Registry size:       "
        f"{decision.registry_size}"
    )
    print(
        "Unmatched issues:    "
        + (
            ", ".join(
                str(index)
                for index
                in decision.unmatched_issue_indexes
            )
            or "—"
        )
    )

    print()
    print(
        f"{'SPECIALIST':24} "
        f"{'SCORE':6} "
        f"{'PRIORITY':8} "
        "MATCH"
    )
    print("-" * 96)

    for item in (
        decision.selected_specialists
    ):
        match_parts = []

        if item.matched_trigger_hints:
            match_parts.append(
                "triggers="
                + "|".join(
                    item.matched_trigger_hints
                )
            )

        if item.matched_domains:
            match_parts.append(
                "domains="
                + "|".join(
                    item.matched_domains
                )
            )

        print(
            f"{item.specialist_slug:24} "
            f"{item.score:<6} "
            f"{item.priority:<8} "
            + "; ".join(
                match_parts
            )
        )

    print()
    print(
        f"Selected specialists: "
        f"{len(decision.selected_specialists)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
