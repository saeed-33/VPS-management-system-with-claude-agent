from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.investigation.contracts import (
    EvidenceKind,
    InvestigationBudget,
    InvestigationFinding,
    SpecialistTaskStatus,
)
from app.agent.investigation.correlation import (
    CrossSpecialistCorrelator,
    DiagnosisCertainty,
)
from app.agent.investigation.investigation_router import (
    InvestigationRoutingDecision,
    SpecialistRoutingMatch,
)
from app.agent.investigation.langgraph_secondary_orchestrator import (
    DynamicSecondaryLangGraphCoordinator,
)
from app.bootstrap import container


class ControlledRecommendationParallelCoordinator:
    """
    Acceptance-only adapter.

    Wave 1 executes for real. After the first successful primary result,
    one controlled secondary recommendation is injected. All subsequent
    Phase 4.17 Registry/budget/routing logic and Specialist execution
    remain real.
    """

    def __init__(
        self,
        *,
        delegate,
        secondary_slug: str,
    ) -> None:
        self._delegate = delegate
        self._secondary_slug = secondary_slug
        self._first_wave_seen = False
        self.recommendation_injected = False

    async def run(self, **kwargs):
        result = await self._delegate.run(**kwargs)

        if self._first_wave_seen:
            return result

        self._first_wave_seen = True

        if not result.runs:
            return result

        first = result.runs[0]

        if (
            first.result.status
            != SpecialistTaskStatus.COMPLETED
        ):
            return result

        controlled_result = replace(
            first.result,
            recommended_next_specialists=(
                self._secondary_slug,
            ),
            metadata={
                **first.result.metadata,
                "acceptance_controlled_recommendation": True,
            },
        )

        controlled_run = replace(
            first,
            result=controlled_result,
        )

        self.recommendation_injected = True

        return replace(
            result,
            runs=(
                controlled_run,
                *result.runs[1:],
            ),
        )


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


def specialist_by_slug(slug: str):
    snapshot = (
        container
        .specialist_registry
        .snapshot()
    )

    specialist = snapshot.get_by_slug(slug)

    if specialist is None:
        available = ", ".join(
            sorted(
                item.slug
                for item in snapshot.definitions
            )
        )
        raise SystemExit(
            f"Specialist {slug!r} is unavailable/enabled. "
            f"Enabled: {available or '—'}"
        )

    return specialist, snapshot


def controlled_initial_decision(
    slug: str,
) -> InvestigationRoutingDecision:
    specialist, snapshot = specialist_by_slug(slug)

    match = SpecialistRoutingMatch(
        specialist_id=specialist.id,
        specialist_slug=specialist.slug,
        specialist_name=specialist.name,
        score=1,
        matched_domains=tuple(specialist.domains),
        matched_trigger_hints=(),
        matched_issue_indexes=(),
        priority=specialist.priority,
    )

    return InvestigationRoutingDecision(
        should_investigate=True,
        reasons=(),
        detected_domains=tuple(specialist.domains),
        candidate_specialists=(match,),
        selected_specialists=(match,),
        unmatched_issue_indexes=(),
        registry_size=len(snapshot.definitions),
        candidate_limit=1,
        selection_limit=1,
    )


def choose_runtime_evidence(result):
    preferred = (
        EvidenceKind.COMMAND_RESULT,
        EvidenceKind.MONITORING_REPORT,
        EvidenceKind.ANALYSIS,
    )

    ordered = []

    for kind in preferred:
        for item in result.state.evidence:
            if (
                item.kind == kind
                and item.evidence_id
                not in {
                    existing.evidence_id
                    for existing in ordered
                }
            ):
                ordered.append(item)

    return tuple(ordered)


def inject_findings(
    result,
    *,
    primary_slug: str,
    secondary_slug: str,
    secondary_state: str,
):
    runs = list(result.runs)

    by_slug = {
        run.specialist_slug: index
        for index, run in enumerate(runs)
    }

    if primary_slug not in by_slug:
        raise RuntimeError(
            f"Primary Specialist {primary_slug!r} "
            "did not execute."
        )

    if secondary_slug not in by_slug:
        raise RuntimeError(
            f"Secondary Specialist {secondary_slug!r} "
            "did not execute."
        )

    evidence = choose_runtime_evidence(result)

    if not evidence:
        raise RuntimeError(
            "Runtime produced no acceptable Evidence "
            "for correlation acceptance."
        )

    primary_evidence = evidence[0].evidence_id
    secondary_evidence = (
        evidence[1].evidence_id
        if len(evidence) > 1
        else evidence[0].evidence_id
    )

    primary_index = by_slug[primary_slug]
    secondary_index = by_slug[secondary_slug]

    primary_run = runs[primary_index]
    secondary_run = runs[secondary_index]

    if (
        primary_run.result.status
        != SpecialistTaskStatus.COMPLETED
    ):
        raise RuntimeError(
            "Primary Specialist did not complete."
        )

    if (
        secondary_run.result.status
        != SpecialistTaskStatus.COMPLETED
    ):
        raise RuntimeError(
            "Secondary Specialist did not complete."
        )

    primary_finding = InvestigationFinding(
        finding_id=(
            f"{result.state.investigation_id}:"
            "acceptance:primary"
        ),
        title="NGINX service presence",
        description=(
            "Controlled correlation fixture backed by "
            "runtime Evidence."
        ),
        confidence=0.95,
        evidence_ids=(primary_evidence,),
        metadata={
            "diagnostic_state": "absent",
            "acceptance_controlled_finding": True,
        },
    )

    secondary_finding = InvestigationFinding(
        finding_id=(
            f"{result.state.investigation_id}:"
            "acceptance:secondary"
        ),
        title="NGINX service presence",
        description=(
            "Controlled correlation fixture backed by "
            "runtime Evidence."
        ),
        confidence=0.90,
        evidence_ids=(secondary_evidence,),
        metadata={
            "diagnostic_state": secondary_state,
            "acceptance_controlled_finding": True,
        },
    )

    runs[primary_index] = replace(
        primary_run,
        result=replace(
            primary_run.result,
            findings=(primary_finding,),
        ),
    )

    runs[secondary_index] = replace(
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


async def run(args) -> int:
    if (
        args.initial_specialist
        == args.secondary_specialist
    ):
        raise SystemExit(
            "Initial and secondary Specialists "
            "must be different."
        )

    specialist_by_slug(args.secondary_specialist)

    parallel = container.langgraph_server_coordinator

    if parallel is None:
        raise SystemExit(
            "Phase 4.16 LangGraph coordinator "
            "is unavailable."
        )

    adapter = (
        ControlledRecommendationParallelCoordinator(
            delegate=parallel,
            secondary_slug=args.secondary_specialist,
        )
    )

    coordinator = (
        DynamicSecondaryLangGraphCoordinator(
            specialist_registry=(
                container.specialist_registry
            ),
            parallel_coordinator=adapter,
        )
    )

    report = (
        container
        .report_query_service
        .get_report(args.report_id)
    )

    analysis = (
        container
        .analysis_repository
        .get_by_report_id(
            args.report_id
        )
    )

    if analysis is None:
        raise SystemExit(
            f"No analysis exists for "
            f"report_id={args.report_id}."
        )

    decision = controlled_initial_decision(
        args.initial_specialist
    )

    print()
    print(
        "# Phase 4.18 Runtime Correlation Acceptance"
    )
    print()
    print(
        f"Report ID:                {report.id}"
    )
    print(
        f"Server ID:                {report.server_id}"
    )
    print(
        f"Primary Specialist:       "
        f"{args.initial_specialist}"
    )
    print(
        f"Secondary Specialist:     "
        f"{args.secondary_specialist}"
    )
    print(
        "4.17 execution:           REAL"
    )
    print(
        "Secondary recommendation: CONTROLLED"
    )
    print(
        "Correlation Findings:     CONTROLLED"
    )
    print(
        "Evidence IDs:             REAL RUNTIME"
    )
    print(
        "Correlator:               REAL 4.18"
    )
    print(
        "Database changed:         NO"
    )

    runtime_result = await coordinator.run(
        server_id=report.server_id,
        report_id=report.id,
        analysis_id=analysis.id,
        routing_decision=decision,
        budget=InvestigationBudget(
            max_specialists=2,
            max_rounds=args.max_rounds,
            max_actions=args.max_actions,
        ),
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
    )

    evidence = choose_runtime_evidence(
        runtime_result
    )

    print()
    print("## RUNTIME INVESTIGATION")
    print()
    print(
        f"Status:                   "
        f"{runtime_result.state.status.value}"
    )
    print(
        f"Specialist runs:          "
        f"{len(runtime_result.runs)}"
    )
    print(
        f"Actions used:             "
        f"{runtime_result.investigation_actions_used}"
        f"/{runtime_result.state.budget.max_actions}"
    )
    print(
        "Executed Specialists:     "
        + ", ".join(
            run.specialist_slug
            for run in runtime_result.runs
        )
    )
    print(
        f"Runtime Evidence items:   "
        f"{len(runtime_result.state.evidence)}"
    )
    print(
        f"Eligible Evidence items:  "
        f"{len(evidence)}"
    )

    correlator = CrossSpecialistCorrelator()

    shared_result = inject_findings(
        runtime_result,
        primary_slug=args.initial_specialist,
        secondary_slug=args.secondary_specialist,
        secondary_state="absent",
    )

    shared = correlator.correlate(
        shared_result
    )

    conflict_result = inject_findings(
        runtime_result,
        primary_slug=args.initial_specialist,
        secondary_slug=args.secondary_specialist,
        secondary_state="present",
    )

    conflict = correlator.correlate(
        conflict_result
    )

    print()
    print("## SHARED-CONCLUSION CORRELATION")
    print()
    print(
        f"Claims:      {len(shared.claims)}"
    )
    print(
        f"Confirmed:   {shared.confirmed_count}"
    )
    print(
        f"Probable:    {shared.probable_count}"
    )
    print(
        f"Unknown:     {shared.unknown_count}"
    )
    print(
        f"Conflicts:   {shared.conflict_count}"
    )

    if shared.claims:
        claim = shared.claims[0]
        print(
            f"Certainty:   {claim.certainty.value}"
        )
        print(
            "Specialists: "
            + ", ".join(
                claim.specialist_slugs
            )
        )
        print(
            "Evidence:    "
            + ", ".join(
                claim.evidence_ids
            )
        )

    print()
    print("## CONFLICT CORRELATION")
    print()
    print(
        f"Claims:      {len(conflict.claims)}"
    )
    print(
        f"Confirmed:   {conflict.confirmed_count}"
    )
    print(
        f"Probable:    {conflict.probable_count}"
    )
    print(
        f"Unknown:     {conflict.unknown_count}"
    )
    print(
        f"Conflicts:   {conflict.conflict_count}"
    )

    if conflict.conflicts:
        item = conflict.conflicts[0]
        print(
            "States:      "
            + ", ".join(
                item.diagnostic_states
            )
        )
        print(
            "Evidence:    "
            + ", ".join(
                item.evidence_ids
            )
        )

    state_evidence_ids = {
        item.evidence_id
        for item in runtime_result.state.evidence
    }

    shared_claim_evidence = {
        evidence_id
        for claim in shared.claims
        for evidence_id in claim.evidence_ids
    }

    conflict_claim_evidence = {
        evidence_id
        for claim in conflict.claims
        for evidence_id in claim.evidence_ids
    }

    executed = {
        run.specialist_slug
        for run in runtime_result.runs
    }

    checks = {
        "runtime_completed": (
            runtime_result.state.status.value
            == "completed"
        ),
        "two_real_specialists_executed": (
            args.initial_specialist in executed
            and args.secondary_specialist in executed
        ),
        "controlled_recommendation_injected": (
            adapter.recommendation_injected
        ),
        "runtime_evidence_available": (
            len(evidence) >= 1
        ),
        "shared_findings_merged": (
            len(shared.claims) == 1
            and len(
                shared.claims[0]
                .specialist_slugs
            ) == 2
        ),
        "shared_claim_confirmed": (
            shared.confirmed_count == 1
            and shared.conflict_count == 0
            and shared.claims[0].certainty
            == DiagnosisCertainty.CONFIRMED
        ),
        "explicit_conflict_detected": (
            conflict.conflict_count == 1
        ),
        "conflict_forces_unknown": (
            conflict.unknown_count == 1
            and conflict.claims[0].certainty
            == DiagnosisCertainty.UNKNOWN
        ),
        "shared_evidence_trace_valid": (
            shared_claim_evidence
            <= state_evidence_ids
        ),
        "conflict_evidence_trace_valid": (
            conflict_claim_evidence
            <= state_evidence_ids
        ),
        "global_action_budget_safe": (
            runtime_result
            .investigation_actions_used
            <= runtime_result
            .state
            .budget
            .max_actions
        ),
    }

    print()
    print("## ACCEPTANCE CHECKS")
    print()

    for name, passed in checks.items():
        print(
            f"- {name}: "
            + (
                "PASS"
                if passed
                else "FAIL"
            )
        )

    print()
    print(
        "NOTE: The two Specialist executions and Evidence "
        "collection are real. Only the recommendation and "
        "the correlation findings are controlled to make "
        "agreement/conflict semantics deterministic."
    )

    return (
        0
        if all(checks.values())
        else 2
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 4.18 deterministic runtime "
            "correlation acceptance."
        )
    )

    parser.add_argument(
        "report_id",
        type=int,
    )

    parser.add_argument(
        "--initial-specialist",
        default="nginx",
    )

    parser.add_argument(
        "--secondary-specialist",
        default="systemd-service",
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

    return asyncio.run(
        run(
            parser.parse_args()
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
