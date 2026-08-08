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
    parser.add_argument("investigation_id")
    args = parser.parse_args()

    item = container.investigation_persistence_service.get(
        args.investigation_id
    )

    if item is None:
        raise SystemExit(f"Investigation not found: {args.investigation_id}")

    print()
    print("Investigation")
    print("=" * 96)
    print(f"Investigation ID:    {item.investigation_id}")
    print(f"Server ID:           {item.server_id}")
    print(f"Report ID:           {item.report_id}")
    print(f"Analysis ID:         {item.analysis_id}")
    print(f"Status:              {item.status}")
    print(f"Should investigate:  {item.should_investigate}")
    print("Reasons:             " + ", ".join(item.routing_reasons))
    print(
        "Detected domains:    "
        + (", ".join(item.detected_domains) or "—")
    )
    print(f"Candidate limit:     {item.candidate_limit}")
    print(f"Selection limit:     {item.selection_limit}")

    print()
    print(
        f"{'RANK':4} {'SPECIALIST':24} "
        f"{'SCORE':6} {'SELECTED':8} {'SEL.RANK':8}"
    )
    print("-" * 96)

    for candidate in item.candidates:
        print(
            f"{candidate.candidate_rank:<4} "
            f"{candidate.specialist_slug:24} "
            f"{candidate.score:<6} "
            f"{str(candidate.is_selected):8} "
            f"{candidate.selected_rank or '-':8}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
