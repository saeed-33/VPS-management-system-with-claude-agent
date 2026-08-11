from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import replace
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.agent.investigation.contracts import (
    EvidenceKind,
    InvestigationBudget,
    InvestigationFinding,
    SpecialistTaskStatus,
)
from app.agent.investigation.correlation import (
    CrossSpecialistCorrelator,
)
from app.agent.investigation.final_diagnosis_synthesizer import (
    FinalDiagnosisSynthesizer,
    create_final_diagnosis_narrative_client,
)
from app.agent.investigation.investigation_router import (
    InvestigationRoutingDecision,
    SpecialistRoutingMatch,
)
from app.bootstrap import container
from app.shared.config import settings


def normalize_issues(value) -> tuple[dict, ...]:
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


def controlled_parallel_decision(
    slugs: tuple[str, ...],
) -> InvestigationRoutingDecision:
    snapshot = container.specialist_registry.snapshot()

    matches = []

    for slug in slugs:
        specialist = snapshot.get_by_slug(slug)

        if specialist is None:
            available = ", ".join(
                sorted(
                    item.slug
                    for item in snapshot.definitions
                )
            )

            raise RuntimeError(
                f"Specialist {slug!r} is unavailable/enabled. "
                f"Enabled: {available or '—'}"
            )

        matches.append(
            SpecialistRoutingMatch(
                specialist_id=specialist.id,
                specialist_slug=specialist.slug,
                specialist_name=specialist.name,
                score=1,
                matched_domains=tuple(
                    specialist.domains
                ),
                matched_trigger_hints=(),
                matched_issue_indexes=(),
                priority=specialist.priority,
            )
        )

    matches_tuple = tuple(matches)

    domains = tuple(
        sorted(
            {
                domain
                for match in matches_tuple
                for domain in match.matched_domains
            }
        )
    )

    return InvestigationRoutingDecision(
        should_investigate=True,
        reasons=(),
        detected_domains=domains,
        candidate_specialists=matches_tuple,
        selected_specialists=matches_tuple,
        unmatched_issue_indexes=(),
        registry_size=len(snapshot.definitions),
        candidate_limit=len(matches_tuple),
        selection_limit=len(matches_tuple),
    )


def choose_runtime_evidence(result):
    preferred = (
        EvidenceKind.COMMAND_RESULT,
        EvidenceKind.MONITORING_REPORT,
        EvidenceKind.ANALYSIS,
    )

    ordered = []
    seen = set()

    for kind in preferred:
        for item in result.state.evidence:
            if (
                item.kind == kind
                and item.evidence_id not in seen
            ):
                seen.add(item.evidence_id)
                ordered.append(item)

    return tuple(ordered)


def inject_controlled_conflict(
    result,
    *,
    primary_slug: str,
    secondary_slug: str,
):
    runs = list(result.runs)

    by_slug = {
        run.specialist_slug: index
        for index, run in enumerate(runs)
    }

    if primary_slug not in by_slug:
        raise RuntimeError(
            f"Primary Specialist {primary_slug!r} did not execute."
        )

    if secondary_slug not in by_slug:
        raise RuntimeError(
            f"Secondary Specialist {secondary_slug!r} did not execute."
        )

    primary_run = runs[by_slug[primary_slug]]
    secondary_run = runs[by_slug[secondary_slug]]

    if primary_run.result.status != SpecialistTaskStatus.COMPLETED:
        raise RuntimeError(
            f"Primary Specialist {primary_slug!r} did not complete."
        )

    if secondary_run.result.status != SpecialistTaskStatus.COMPLETED:
        raise RuntimeError(
            f"Secondary Specialist {secondary_slug!r} did not complete."
        )

    evidence = choose_runtime_evidence(result)

    if not evidence:
        raise RuntimeError(
            "Runtime produced no acceptable Evidence."
        )

    first_id = evidence[0].evidence_id

    second_id = (
        evidence[1].evidence_id
        if len(evidence) > 1
        else first_id
    )

    primary_finding = InvestigationFinding(
        finding_id=(
            f"{result.state.investigation_id}:"
            "sample:primary"
        ),
        title="NGINX service presence",
        description=(
            "Controlled evaluation finding "
            "backed by real runtime Evidence."
        ),
        confidence=0.95,
        evidence_ids=(first_id,),
        metadata={
            "diagnostic_state": "absent",
            "evaluation_controlled_finding": True,
        },
    )

    secondary_finding = InvestigationFinding(
        finding_id=(
            f"{result.state.investigation_id}:"
            "sample:secondary"
        ),
        title="NGINX service presence",
        description=(
            "Controlled evaluation finding "
            "backed by real runtime Evidence."
        ),
        confidence=0.90,
        evidence_ids=(second_id,),
        metadata={
            "diagnostic_state": "present",
            "evaluation_controlled_finding": True,
        },
    )

    runs[by_slug[primary_slug]] = replace(
        primary_run,
        result=replace(
            primary_run.result,
            findings=(primary_finding,),
        ),
    )

    runs[by_slug[secondary_slug]] = replace(
        secondary_run,
        result=replace(
            secondary_run.result,
            findings=(secondary_finding,),
        ),
    )

    return replace(
        result,
        runs=tuple(runs),
    )


def current_runtime_counts(
    *,
    limit: int = 500,
) -> tuple[int, int]:
    summaries = (
        container.investigation_read_service
        .list_recent(
            limit=limit,
            server_id=None,
        )
    )

    runtime_count = 0
    real_conflict_count = 0

    for summary in summaries:
        detail = (
            container.investigation_read_service
            .get(
                summary.investigation_id
            )
        )

        if (
            detail is None
            or not detail.runtime_available
            or detail.runtime is None
        ):
            continue

        runtime_count += 1

        conflicts = (
            detail.runtime.conflicts
            or ()
        )

        if any(
            isinstance(item, dict)
            and item.get("conflict_id")
            for item in conflicts
        ):
            real_conflict_count += 1

    return (
        runtime_count,
        real_conflict_count,
    )


async def run_one_sample(
    *,
    sample_index: int,
    report,
    analysis,
    budget: InvestigationBudget,
    decision: InvestigationRoutingDecision,
    primary_slug: str,
    secondary_slug: str,
    inject_conflict: bool,
):
    persisted = (
        container.investigation_persistence_service
        .persist_routing_decision(
            server_id=report.server_id,
            report_id=report.id,
            analysis_id=analysis.id,
            decision=decision,
            budget=budget,
            routing_version=(
                "evaluation-4.20.6"
            ),
        )
    )

    investigation_id = (
        persisted.investigation_id
    )

    print()
    print(
        f"## SAMPLE {sample_index}"
    )
    print(
        f"Investigation ID:     "
        f"{investigation_id}"
    )
    print(
        f"Conflict fixture:     "
        f"{inject_conflict}"
    )

    parallel = (
        container.langgraph_server_coordinator
    )

    if parallel is None:
        raise RuntimeError(
            "LangGraph server coordinator is unavailable."
        )

    runtime_result = await parallel.run(
        server_id=report.server_id,
        report_id=report.id,
        analysis_id=analysis.id,
        routing_decision=decision,
        budget=budget,
        initial_analysis_summary=getattr(
            analysis,
            "summary",
            None,
        ),
        initial_analysis_issues=normalize_issues(
            getattr(
                analysis,
                "issues",
                None,
            )
        ),
        investigation_id=investigation_id,
    )

    executed = {
        run.specialist_slug
        for run in runtime_result.runs
    }

    expected = {
        primary_slug,
        secondary_slug,
    }

    if not expected <= executed:
        raise RuntimeError(
            "Expected Specialists were not both executed. "
            f"expected={sorted(expected)} "
            f"executed={sorted(executed)}"
        )

    completed = all(
        run.result.status
        == SpecialistTaskStatus.COMPLETED
        for run in runtime_result.runs
    )

    if not completed:
        raise RuntimeError(
            "At least one Specialist did not complete."
        )

    correlated_input = runtime_result

    if inject_conflict:
        correlated_input = (
            inject_controlled_conflict(
                runtime_result,
                primary_slug=primary_slug,
                secondary_slug=secondary_slug,
            )
        )

    diagnosis = (
        CrossSpecialistCorrelator()
        .correlate(
            correlated_input
        )
    )

    narrative_client = (
        create_final_diagnosis_narrative_client(
            settings
        )
    )

    try:
        narrative = await FinalDiagnosisSynthesizer(
            client=narrative_client
        ).synthesize(
            diagnosis
        )
    finally:
        close = getattr(
            narrative_client,
            "close",
            None,
        )

        if callable(close):
            await close()

    persisted_after_runtime = (
        container
        .investigation_runtime_snapshot_service
        .persist(
            investigation_id=investigation_id,
            coordinator_result=correlated_input,
            final_diagnosis=diagnosis,
            narrative=narrative,
        )
    )

    print(
        f"Status:               "
        f"{persisted_after_runtime.status}"
    )
    print(
        f"Specialist runs:      "
        f"{len(runtime_result.runs)}"
    )
    print(
        f"Evidence:             "
        f"{len(runtime_result.state.evidence)}"
    )
    print(
        f"Actions:              "
        f"{runtime_result.investigation_actions_used}"
        f"/{budget.max_actions}"
    )
    print(
        f"Claims:               "
        f"{len(diagnosis.claims)}"
    )
    print(
        f"Conflicts:            "
        f"{len(diagnosis.conflicts)}"
    )
    print(
        f"Narrative fallback:   "
        f"{narrative.used_fallback}"
    )

    return investigation_id


async def run(args) -> int:
    if not settings.llm_enabled:
        raise SystemExit(
            "LLM is disabled."
        )

    if (
        args.primary_specialist
        == args.secondary_specialist
    ):
        raise SystemExit(
            "Primary and secondary Specialists must differ."
        )

    report = (
        container.report_query_service
        .get_report(
            args.report_id
        )
    )

    analysis = (
        container.analysis_repository
        .get_by_report_id(
            args.report_id
        )
    )

    if analysis is None:
        raise SystemExit(
            f"No analysis for report_id={args.report_id}."
        )

    runtime_count, conflict_count = (
        current_runtime_counts()
    )

    required_runtime = max(
        0,
        args.runtime_target
        - runtime_count,
    )

    required_conflicts = max(
        0,
        args.conflict_target
        - conflict_count,
    )

    samples_to_run = min(
        required_runtime,
        args.max_new,
    )

    print()
    print(
        "# Phase 4.20.6 Runtime Sample Expansion"
    )
    print()
    print(
        f"Existing runtime snapshots: "
        f"{runtime_count}"
    )
    print(
        f"Existing conflict snapshots: "
        f"{conflict_count}"
    )
    print(
        f"Runtime target:              "
        f"{args.runtime_target}"
    )
    print(
        f"Conflict target:             "
        f"{args.conflict_target}"
    )
    print(
        f"New samples required:        "
        f"{required_runtime}"
    )
    print(
        f"New conflict samples needed: "
        f"{required_conflicts}"
    )
    print(
        f"Samples scheduled this run:  "
        f"{samples_to_run}"
    )
    print()
    print(
        "WARNING: each scheduled sample runs "
        "real LangGraph Specialists, Ollama, SSH, "
        "diagnostic tools, correlation, narrative, "
        "and database persistence."
    )

    if samples_to_run == 0:
        print()
        print(
            "Runtime sample target is already met."
        )
        return 0

    budget = InvestigationBudget(
        max_specialists=2,
        max_rounds=args.max_rounds,
        max_actions=args.max_actions,
    )

    decision = controlled_parallel_decision(
        (
            args.primary_specialist,
            args.secondary_specialist,
        )
    )

    created = []
    failed = []

    for index in range(
        1,
        samples_to_run + 1,
    ):
        inject_conflict = (
            index
            <= required_conflicts
        )

        try:
            investigation_id = (
                await run_one_sample(
                    sample_index=index,
                    report=report,
                    analysis=analysis,
                    budget=budget,
                    decision=decision,
                    primary_slug=(
                        args.primary_specialist
                    ),
                    secondary_slug=(
                        args.secondary_specialist
                    ),
                    inject_conflict=(
                        inject_conflict
                    ),
                )
            )

            created.append(
                investigation_id
            )

        except Exception as exc:
            failed.append(
                (
                    index,
                    type(exc).__name__,
                    str(exc),
                )
            )

            print()
            print(
                f"Sample {index} FAILED: "
                f"{type(exc).__name__}: {exc}"
            )

            if args.stop_on_failure:
                break

    after_runtime, after_conflicts = (
        current_runtime_counts()
    )

    print()
    print("## EXPANSION SUMMARY")
    print()
    print(
        f"Successful new snapshots: "
        f"{len(created)}"
    )
    print(
        f"Failed attempts:           "
        f"{len(failed)}"
    )
    print(
        f"Runtime snapshots now:    "
        f"{after_runtime}/"
        f"{args.runtime_target}"
    )
    print(
        f"Conflict snapshots now:   "
        f"{after_conflicts}/"
        f"{args.conflict_target}"
    )

    if created:
        print()
        print(
            "Persisted Investigation IDs:"
        )

        for item in created:
            print(
                f"- {item}"
            )

    if failed:
        print()
        print("Failures:")

        for index, name, message in failed:
            print(
                f"- sample {index}: "
                f"{name}: {message}"
            )

    target_met = (
        after_runtime
        >= args.runtime_target
        and after_conflicts
        >= args.conflict_target
    )

    print()
    print(
        "Phase 4.20.6 sample target: "
        + (
            "PASS"
            if target_met
            else "NOT YET MET"
        )
    )

    print()
    print(
        "Next command after target is met:"
    )
    print(
        "uv run python "
        "tools/run_production_readiness_evaluation.py "
        "--limit 500"
    )

    return (
        0
        if target_met
        else 2
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate additional real persisted "
            "runtime evaluation samples."
        )
    )

    parser.add_argument(
        "report_id",
        nargs="?",
        type=int,
        default=1076,
    )

    parser.add_argument(
        "--primary-specialist",
        default="nginx",
    )

    parser.add_argument(
        "--secondary-specialist",
        default="systemd-service",
    )

    parser.add_argument(
        "--runtime-target",
        type=int,
        default=10,
    )

    parser.add_argument(
        "--conflict-target",
        type=int,
        default=5,
    )

    parser.add_argument(
        "--max-new",
        type=int,
        default=9,
    )

    parser.add_argument(
        "--max-rounds",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--max-actions",
        type=int,
        default=10,
    )

    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
    )

    return asyncio.run(
        run(
            parser.parse_args()
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
