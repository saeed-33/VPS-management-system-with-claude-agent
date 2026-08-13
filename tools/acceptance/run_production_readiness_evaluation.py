from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from tools.acceptance.evaluation.aggregate_readiness import (
    AggregateReadinessEvaluator,
)
from tools.acceptance.evaluation.persisted_runtime import (
    PersistedRuntimeEvaluator,
)
from tools.acceptance.evaluation.safety_runtime import (
    evaluate_safety_runtime,
)
from app.composition import container


async def run(args) -> int:
    summaries = (
        container.investigation_read_service
        .list_recent(
            limit=args.limit,
            server_id=args.server_id,
        )
    )

    persisted_evaluator = (
        PersistedRuntimeEvaluator()
    )

    persisted_observations = []
    runtime_snapshots = 0
    skipped = 0

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

        evaluated = (
            persisted_evaluator.evaluate(
                detail
            )
        )

        if evaluated.observations:
            runtime_snapshots += 1
            persisted_observations.extend(
                evaluated.observations
            )

    safety_observations = (
        await evaluate_safety_runtime()
    )

    aggregate = (
        AggregateReadinessEvaluator()
        .evaluate(
            persisted_observations=tuple(
                persisted_observations
            ),
            safety_observations=(
                safety_observations
            ),
        )
    )

    print()
    print(
        "# Phase 4.20.5 "
        "Aggregate Production Readiness"
    )
    print()
    print(
        f"Investigations scanned:       "
        f"{len(summaries)}"
    )
    print(
        f"Runtime snapshots evaluated:  "
        f"{runtime_snapshots}"
    )
    print(
        f"Without runtime snapshot:     "
        f"{skipped}"
    )
    print(
        f"Persisted observations:       "
        f"{len(persisted_observations)}"
    )
    print(
        f"Safety observations:          "
        f"{len(safety_observations)}"
    )
    print(
        f"Total observations:           "
        f"{len(aggregate.observations)}"
    )

    print()
    print("## READINESS METRICS")
    print()

    report_metrics = []

    for metric in (
        aggregate.readiness.metrics
    ):
        status = (
            "PASS"
            if metric.threshold_met
            else (
                "BLOCK"
                if metric.hard_block_triggered
                else "INSUFFICIENT"
            )
        )

        deficit = (
            aggregate.sample_deficits[
                metric.metric
            ]
        )

        print(
            f"- {metric.metric.value}"
        )
        print(
            f"  samples: "
            f"{metric.samples}/"
            f"{metric.required_samples}"
        )
        print(
            f"  pass rate: "
            f"{metric.pass_rate:.3f} "
            f"(required "
            f"{metric.required_pass_rate:.3f})"
        )
        print(
            f"  result: {status}"
        )

        if deficit:
            print(
                f"  additional samples needed: "
                f"{deficit}"
            )

        report_metrics.append(
            {
                "metric": (
                    metric.metric.value
                ),
                "samples": metric.samples,
                "required_samples": (
                    metric.required_samples
                ),
                "passed_samples": (
                    metric.passed_samples
                ),
                "pass_rate": metric.pass_rate,
                "required_pass_rate": (
                    metric.required_pass_rate
                ),
                "threshold_met": (
                    metric.threshold_met
                ),
                "hard_block_triggered": (
                    metric.hard_block_triggered
                ),
                "additional_samples_needed": (
                    deficit
                ),
            }
        )

    print()
    print("## READINESS DECISION")
    print()
    print(
        f"Status:                 "
        f"{aggregate.readiness.status.value}"
    )
    print(
        "Automatic remediation:  "
        f"{aggregate.readiness.automatic_remediation_allowed}"
    )

    if (
        aggregate.readiness
        .blocking_reasons
    ):
        print()
        print("Blocking reasons:")

        for reason in (
            aggregate.readiness
            .blocking_reasons
        ):
            print(
                f"- {reason}"
            )

    output_path = (
        PROJECT_ROOT
        / args.output
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "phase": "4.20.5",
        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "runtime_snapshots_evaluated": (
            runtime_snapshots
        ),
        "persisted_observations": (
            len(persisted_observations)
        ),
        "safety_observations": (
            len(safety_observations)
        ),
        "total_observations": (
            len(aggregate.observations)
        ),
        "readiness_status": (
            aggregate.readiness.status.value
        ),
        "automatic_remediation_allowed": (
            aggregate.readiness
            .automatic_remediation_allowed
        ),
        "blocking_reasons": list(
            aggregate.readiness
            .blocking_reasons
        ),
        "metrics": report_metrics,
    }

    output_path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        f"Machine-readable report: "
        f"{output_path.relative_to(PROJECT_ROOT)}"
    )

    print()
    print(
        "Phase 4.20.5 aggregation: PASS"
    )

    if (
        aggregate.readiness.status.value
        == "ready_for_supervised_operations"
    ):
        print(
            "Production Readiness Gate: PASS"
        )
    else:
        print(
            "Production Readiness Gate: "
            "NOT YET PASSED"
        )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Aggregate Phase 4.20 persisted "
            "runtime + safety evaluation."
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

    parser.add_argument(
        "--output",
        default=(
            "artifacts/evaluation/"
            "phase_4_20_readiness.json"
        ),
    )

    return asyncio.run(
        run(
            parser.parse_args()
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
