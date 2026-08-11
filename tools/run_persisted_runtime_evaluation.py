from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.domain.evaluation import (
    ProductionReadinessGate,
)
from app.domain.evaluation.persisted_runtime import (
    PersistedRuntimeEvaluator,
)
from app.bootstrap import container


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate persisted Investigation "
            "runtime snapshots."
        )
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
    )

    parser.add_argument(
        "--server-id",
        type=int,
        default=None,
    )

    args = parser.parse_args()

    summaries = (
        container.investigation_read_service
        .list_recent(
            limit=args.limit,
            server_id=args.server_id,
        )
    )

    evaluator = PersistedRuntimeEvaluator()

    observations = []
    evaluated = 0
    skipped = 0

    print()
    print(
        "# Phase 4.20.3 "
        "Persisted Runtime Evaluation"
    )
    print()
    print(
        f"Investigations scanned:  "
        f"{len(summaries)}"
    )

    for summary in summaries:
        detail = (
            container
            .investigation_read_service
            .get(
                summary.investigation_id
            )
        )

        if (
            detail is None
            or not detail.runtime_available
        ):
            skipped += 1
            continue

        result = evaluator.evaluate(
            detail
        )

        observations.extend(
            result.observations
        )

        evaluated += 1

        passed = sum(
            1
            for item
            in result.observations
            if item.passed
        )

        print()
        print(
            f"## {detail.investigation_id}"
        )
        print(
            f"Status:              "
            f"{detail.status}"
        )
        print(
            f"Runtime available:   "
            f"{detail.runtime_available}"
        )
        print(
            f"Observations:        "
            f"{passed}/"
            f"{len(result.observations)} "
            "passed"
        )

        for item in (
            result.observations
        ):
            print(
                f"- {item.metric.value}: "
                + (
                    "PASS"
                    if item.passed
                    else "FAIL"
                )
            )

            if item.details:
                print(
                    f"  {item.details}"
                )

    readiness = (
        ProductionReadinessGate()
        .evaluate(
            tuple(observations)
        )
    )

    counts = Counter(
        item.metric.value
        for item in observations
    )

    print()
    print("## SUMMARY")
    print()
    print(
        f"Runtime snapshots evaluated: "
        f"{evaluated}"
    )
    print(
        f"Without runtime snapshot:     "
        f"{skipped}"
    )
    print(
        f"Observations emitted:         "
        f"{len(observations)}"
    )
    print(
        f"Readiness status:             "
        f"{readiness.status.value}"
    )
    print(
        "Automatic remediation:       "
        f"{readiness.automatic_remediation_allowed}"
    )

    print()
    print("## MEASURED METRICS")
    print()

    if not counts:
        print("- none")
    else:
        for name in sorted(counts):
            print(
                f"- {name}: "
                f"{counts[name]}"
            )

    print()
    print("## BLOCKING / MISSING COVERAGE")
    print()

    if readiness.blocking_reasons:
        for reason in (
            readiness.blocking_reasons
        ):
            print(
                f"- {reason}"
            )
    else:
        print("- none")

    print()
    print(
        "NOTE: A status of "
        "'insufficient_evidence' is expected "
        "until enough real runtime samples "
        "and Phase 4.20.4 safety/provider/"
        "routing observations exist."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
