from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

PROJECT_ROOT = Path(__file__).resolve().parents[1]
project_root_value = str(PROJECT_ROOT)
if project_root_value not in sys.path:
    sys.path.insert(0, project_root_value)

from sqlalchemy import select

from app.shared.database.models.report_analysis import (
    ReportAnalysisModel,
)
from app.shared.database.session import SessionLocal


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None

    ordered = sorted(values)
    index = int(round((len(ordered) - 1) * pct))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()

    with SessionLocal() as session:
        rows = list(
            session.scalars(
                select(ReportAnalysisModel)
                .where(ReportAnalysisModel.status == "completed")
                .order_by(ReportAnalysisModel.id.desc())
                .limit(args.limit)
            ).all()
        )

    by_source = defaultdict(lambda: defaultdict(list))

    profiled = 0
    for row in rows:
        metrics = row.performance_metrics or {}
        timings = metrics.get("timings_ms") or {}
        if not timings:
            continue

        profiled += 1

        for name, value in timings.items():
            if isinstance(value, (int, float)):
                by_source[row.analysis_source][name].append(
                    float(value)
                )

    output = {
        "analyses_profiled": profiled,
        "sources": {},
    }

    print()
    print("RAG Performance Profile")
    print("=" * 44)
    print(f"Profiled analyses: {profiled}")

    for source, timings in sorted(by_source.items()):
        print()
        print(source)
        print("-" * len(source))

        source_result = {}

        for name, values in sorted(timings.items()):
            result = {
                "count": len(values),
                "mean_ms": round(mean(values), 2),
                "median_ms": round(median(values), 2),
                "p95_ms": round(
                    percentile(values, 0.95) or 0.0,
                    2,
                ),
            }
            source_result[name] = result

            print(
                f"{name:30} "
                f"avg={result['mean_ms']:9.2f} ms  "
                f"p50={result['median_ms']:9.2f}  "
                f"p95={result['p95_ms']:9.2f}"
            )

        output["sources"][source] = source_result

    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print()
        print(f"JSON report: {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
