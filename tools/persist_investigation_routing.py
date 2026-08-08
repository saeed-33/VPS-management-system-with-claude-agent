from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.bootstrap import container


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report_id", type=int)
    args = parser.parse_args()

    report = container.report_query_service.get_report(args.report_id)
    analysis = container.analysis_repository.get_by_report_id(args.report_id)

    if analysis is None:
        raise SystemExit(f"No analysis exists for report_id={args.report_id}.")

    decision = container.investigation_router.route(
        report=report,
        analysis=analysis,
    )

    investigation = (
        container.investigation_persistence_service.persist_routing_decision(
            server_id=report.server_id,
            report_id=report.id,
            analysis_id=analysis.id,
            decision=decision,
        )
    )

    print()
    print("Investigation persisted")
    print("=" * 72)
    print(f"Investigation ID: {investigation.investigation_id}")
    print(f"Candidates:       {len(investigation.candidates)}")
    print(
        "Selected:         "
        f"{sum(1 for item in investigation.candidates if item.is_selected)}"
    )
    print()
    print(
        "Inspect with:\n"
        "  uv run python tools/inspect_investigation.py "
        f"{investigation.investigation_id}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
