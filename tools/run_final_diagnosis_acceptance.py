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
)
from app.agent.investigation.final_diagnosis_synthesizer import (
    FinalDiagnosisSynthesizer,
    create_final_diagnosis_narrative_client,
)
from app.agent.investigation.investigation_router import (
    InvestigationRoutingDecision,
    SpecialistRoutingMatch,
)
from app.agent.investigation.langgraph_secondary_orchestrator import (
    DynamicSecondaryLangGraphCoordinator,
)
from app.bootstrap import container
from app.shared.config import settings


class ControlledRecommendationParallelCoordinator:
    """
    Acceptance-only adapter.

    Primary and secondary Specialist execution remain real.
    Only the first secondary recommendation is controlled so that
    the two-Specialist runtime path is deterministic.
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
    snapshot = container.specialist_registry.snapshot()
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


def inject_controlled_conflict_findings(
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

    evidence = choose_runtime_evidence(result)

    if not evidence:
        raise RuntimeError(
            "Runtime produced no acceptable Evidence."
        )

    first_evidence_id = evidence[0].evidence_id
    second_evidence_id = (
        evidence[1].evidence_id
        if len(evidence) > 1
        else first_evidence_id
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
            "Controlled final-diagnosis fixture backed "
            "by real runtime Evidence."
        ),
        confidence=0.95,
        evidence_ids=(first_evidence_id,),
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
            "Controlled final-diagnosis fixture backed "
            "by real runtime Evidence."
        ),
        confidence=0.90,
        evidence_ids=(second_evidence_id,),
        metadata={
            "diagnostic_state": "present",
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
    if not settings.llm_enabled:
        raise SystemExit(
            "LLM is disabled; runtime narrative acceptance "
            "requires the configured provider."
        )

    if (
        args.initial_specialist
        == args.secondary_specialist
    ):
        raise SystemExit(
            "Initial and secondary Specialists must differ."
        )

    specialist_by_slug(args.secondary_specialist)

    parallel = container.langgraph_server_coordinator

    if parallel is None:
        raise SystemExit(
            "Phase 4.16 LangGraph coordinator is unavailable."
        )

    adapter = ControlledRecommendationParallelCoordinator(
        delegate=parallel,
        secondary_slug=args.secondary_specialist,
    )

    coordinator = DynamicSecondaryLangGraphCoordinator(
        specialist_registry=container.specialist_registry,
        parallel_coordinator=adapter,
    )

    report = container.report_query_service.get_report(
        args.report_id
    )

    analysis = (
        container.analysis_repository.get_by_report_id(
            args.report_id
        )
    )

    if analysis is None:
        raise SystemExit(
            f"No analysis exists for report_id={args.report_id}."
        )

    decision = controlled_initial_decision(
        args.initial_specialist
    )

    print()
    print("# Phase 4.18 Final Diagnosis Runtime Acceptance")
    print()
    print(f"Report ID:                {report.id}")
    print(f"Server ID:                {report.server_id}")
    print(
        f"Primary Specialist:       "
        f"{args.initial_specialist}"
    )
    print(
        f"Secondary Specialist:     "
        f"{args.secondary_specialist}"
    )
    print(
        f"Narrative provider:       "
        f"{settings.llm_provider}"
    )
    print(
        "4.17 execution:           REAL"
    )
    print(
        "Secondary recommendation: CONTROLLED"
    )
    print(
        "Correlation findings:     CONTROLLED"
    )
    print(
        "Evidence IDs:             REAL RUNTIME"
    )
    print(
        "Correlator:               REAL 4.18"
    )
    print(
        "Narrative synthesis:      REAL PROVIDER"
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

    controlled_result = inject_controlled_conflict_findings(
        runtime_result,
        primary_slug=args.initial_specialist,
        secondary_slug=args.secondary_specialist,
    )

    diagnosis = CrossSpecialistCorrelator().correlate(
        controlled_result
    )

    narrative_client = (
        create_final_diagnosis_narrative_client(
            settings
        )
    )

    synthesizer = FinalDiagnosisSynthesizer(
        client=narrative_client
    )

    try:
        narrative = await synthesizer.synthesize(
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

    fallback = await FinalDiagnosisSynthesizer().synthesize(
        diagnosis
    )

    print()
    print("## DETERMINISTIC FINAL DIAGNOSIS")
    print()
    print(
        f"Claims:                   "
        f"{len(diagnosis.claims)}"
    )
    print(
        f"Confirmed:                "
        f"{diagnosis.confirmed_count}"
    )
    print(
        f"Probable:                 "
        f"{diagnosis.probable_count}"
    )
    print(
        f"Unknown:                  "
        f"{diagnosis.unknown_count}"
    )
    print(
        f"Conflicts:                "
        f"{diagnosis.conflict_count}"
    )
    print(
        f"Evidence IDs:             "
        f"{len(diagnosis.evidence_ids)}"
    )

    print()
    print("## REAL PROVIDER NARRATIVE")
    print()
    print(
        f"Provider/model:           "
        f"{narrative.provider_name}/"
        f"{narrative.model_name}"
    )
    print(
        f"Used fallback:            "
        f"{narrative.used_fallback}"
    )
    print(
        "Claim IDs:                "
        + (
            ", ".join(narrative.claim_ids)
            or "—"
        )
    )
    print(
        "Conflict IDs:             "
        + (
            ", ".join(narrative.conflict_ids)
            or "—"
        )
    )
    print()
    print(narrative.summary)

    if narrative.operator_notes:
        print()
        print("Operator notes:")
        for note in narrative.operator_notes:
            print(f"- {note}")

    print()
    print("## DETERMINISTIC FALLBACK")
    print()
    print(
        f"Used fallback:            "
        f"{fallback.used_fallback}"
    )
    print(
        "Claim IDs:                "
        + (
            ", ".join(fallback.claim_ids)
            or "—"
        )
    )
    print(
        "Conflict IDs:             "
        + (
            ", ".join(fallback.conflict_ids)
            or "—"
        )
    )

    allowed_claim_ids = {
        claim.claim_id
        for claim in diagnosis.claims
    }

    allowed_conflict_ids = {
        conflict.conflict_id
        for conflict in diagnosis.conflicts
    }

    narrative_claim_ids = set(
        narrative.claim_ids
    )
    narrative_conflict_ids = set(
        narrative.conflict_ids
    )

    fallback_claim_ids = set(
        fallback.claim_ids
    )
    fallback_conflict_ids = set(
        fallback.conflict_ids
    )

    executed = {
        run.specialist_slug
        for run in runtime_result.runs
    }

    state_evidence_ids = {
        item.evidence_id
        for item in runtime_result.state.evidence
    }

    diagnosis_evidence_ids = set(
        diagnosis.evidence_ids
    )

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
        "conflict_diagnosis_built": (
            diagnosis.conflict_count == 1
            and diagnosis.unknown_count == 1
        ),
        "diagnosis_evidence_trace_valid": (
            diagnosis_evidence_ids
            <= state_evidence_ids
        ),
        "narrative_claim_ids_valid": (
            narrative_claim_ids
            <= allowed_claim_ids
        ),
        "narrative_conflict_ids_valid": (
            narrative_conflict_ids
            <= allowed_conflict_ids
        ),
        "narrative_preserves_conflicts": (
            not allowed_conflict_ids
            or allowed_conflict_ids
            <= narrative_conflict_ids
        ),
        "provider_or_safe_fallback": (
            (
                narrative.used_fallback
                and narrative.summary
                == diagnosis.summary
            )
            or (
                not narrative.used_fallback
                and bool(
                    narrative.summary.strip()
                )
            )
        ),
        "deterministic_fallback_available": (
            fallback.used_fallback
            and fallback_claim_ids
            == allowed_claim_ids
            and fallback_conflict_ids
            == allowed_conflict_ids
            and fallback.summary
            == diagnosis.summary
        ),
        "global_action_budget_safe": (
            runtime_result.investigation_actions_used
            <= runtime_result.state.budget.max_actions
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
        "NOTE: The LLM may only narrate validated diagnosis "
        "objects. A provider/validation failure is accepted "
        "only when the deterministic fallback is returned."
    )

    return (
        0
        if all(checks.values())
        else 2
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 4.18 real-provider final diagnosis acceptance."
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
