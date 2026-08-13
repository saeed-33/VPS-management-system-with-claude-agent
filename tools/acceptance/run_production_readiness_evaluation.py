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
from app.runtime.claude.observability import (
    ClaudeAgentObservabilityService,
)


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

    observability = ClaudeAgentObservabilityService(
        container.agent_job_repository
    )
    runtime_traces = observability.list_recent_traces(
        limit=500,
        server_id=args.server_id,
    )
    completed_runtime_traces = [
        trace
        for trace in runtime_traces
        if trace["status"] == "completed"
        and trace.get("session_id")
    ]

    evaluated_details = []
    for summary in summaries:
        detail = (
            container.investigation_read_service.get(
                summary.investigation_id
            )
        )
        if detail is not None and detail.runtime_available:
            evaluated_details.append(detail)

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
        "# C.14.12 "
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
                "numerator": metric.passed_samples,
                "denominator": metric.samples,
                "score": metric.pass_rate,
                "threshold": metric.required_pass_rate,
                "result": (
                    "PASS"
                    if metric.threshold_met
                    else "FAIL"
                ),
                "supporting_observation_ids": [
                    item.case_id
                    for item in aggregate.observations
                    if item.metric == metric.metric
                ],
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
        "phase": "C.14.12",
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
        "runtime_sessions": len(
            completed_runtime_traces
        ),
        "persisted_runtime_observations": len(
            persisted_observations
        ),
        "controlled_safety_observations": len(
            safety_observations
        ),
        "aggregate_observations": len(
            aggregate.observations
        ),
        "observation_counts": {
            "reports": len({
                detail.report_id
                for detail in evaluated_details
            }),
            "analyses": len({
                detail.analysis_id
                for detail in evaluated_details
                if detail.analysis_id is not None
            }),
            "investigations": len(evaluated_details),
            "specialist_runs": sum(
                len(detail.runtime.specialist_runs)
                for detail in evaluated_details
                if detail.runtime is not None
            ),
            "evidence_records": sum(
                len(detail.runtime.evidence)
                for detail in evaluated_details
                if detail.runtime is not None
            ),
            "controlled_failures": len(
                safety_observations
            ),
        },
        "real_runtime_observations": [
            {
                "agent_job_id": trace["job_id"],
                "session_id": trace.get("session_id"),
                "server_id": trace.get("server_id"),
                "model": trace.get("model_usage", {}),
                "turn_count": trace.get("turn_count"),
                "tool_call_count": trace.get("tool_call_count"),
                "mcp_servers": trace.get("mcp_servers", []),
                "mcp_connected": trace.get("mcp_connected"),
                "duration_ms": trace.get("duration_ms"),
                "result": trace.get("status"),
            }
            for trace in completed_runtime_traces
        ],
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
        "C.14.12 aggregation: PASS"
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
            "Aggregate C.14.12 persisted "
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
            "c14_12_readiness.json"
        ),
    )

    return asyncio.run(
        run(
            parser.parse_args()
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
