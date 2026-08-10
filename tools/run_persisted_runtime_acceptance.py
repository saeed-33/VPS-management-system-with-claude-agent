from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient


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
from app.bootstrap import container
from app.main import app
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

    matches: list[SpecialistRoutingMatch] = []

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

    detected_domains = tuple(
        sorted(
            {
                domain
                for match in matches_tuple
                for domain
                in match.matched_domains
            }
        )
    )

    return InvestigationRoutingDecision(
        should_investigate=True,
        reasons=(),
        detected_domains=detected_domains,
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

    first_evidence_id = evidence[0].evidence_id
    second_evidence_id = (
        evidence[1].evidence_id
        if len(evidence) > 1
        else first_evidence_id
    )

    primary_finding = InvestigationFinding(
        finding_id=(
            f"{result.state.investigation_id}:"
            "acceptance:primary"
        ),
        title="NGINX service presence",
        description=(
            "Controlled correlation fixture backed "
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
            "Controlled correlation fixture backed "
            "by real runtime Evidence."
        ),
        confidence=0.90,
        evidence_ids=(second_evidence_id,),
        metadata={
            "diagnostic_state": "present",
            "acceptance_controlled_finding": True,
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


def record_check(
    checks: dict[str, bool],
    name: str,
    passed: bool,
    detail: str = "",
) -> None:
    checks[name] = bool(passed)

    print(
        f"- {name}: "
        + ("PASS" if passed else "FAIL")
    )

    if detail:
        print(f"  {detail}")


async def run(args) -> int:
    if not settings.llm_enabled:
        raise SystemExit(
            "LLM is disabled; this acceptance requires "
            "the configured narrative provider."
        )

    if args.initial_specialist == args.secondary_specialist:
        raise SystemExit(
            "Initial and secondary Specialists must differ."
        )

    parallel = container.langgraph_server_coordinator

    if parallel is None:
        raise SystemExit(
            "Phase 4.16 LangGraph coordinator is unavailable."
        )

    report = container.report_query_service.get_report(
        args.report_id
    )

    analysis = container.analysis_repository.get_by_report_id(
        args.report_id
    )

    if analysis is None:
        raise SystemExit(
            f"No analysis exists for report_id={args.report_id}."
        )

    budget = InvestigationBudget(
        max_specialists=2,
        max_rounds=args.max_rounds,
        max_actions=args.max_actions,
    )

    decision = controlled_parallel_decision(
        (
            args.initial_specialist,
            args.secondary_specialist,
        )
    )

    print()
    print(
        "# Phase 4.19.6-v2 Persisted Runtime Snapshot Acceptance"
    )
    print()
    print(f"Report ID:                 {report.id}")
    print(f"Server ID:                 {report.server_id}")
    print(f"Analysis ID:               {analysis.id}")
    print(
        f"Specialists:               "
        f"{args.initial_specialist}, "
        f"{args.secondary_specialist}"
    )
    print(
        f"Narrative provider:        "
        f"{settings.llm_provider}"
    )
    print("Initial Specialist set:    CONTROLLED ACCEPTANCE")
    print("LangGraph parallel:        REAL")
    print("Specialist execution:      REAL")
    print("Policy/SSH/tools:           REAL")
    print("Runtime Evidence:          REAL")
    print("Correlation findings:      CONTROLLED")
    print("Final Diagnosis:           REAL CORRELATOR")
    print("Narrative:                 REAL PROVIDER")
    print("Snapshot persistence:      REAL DATABASE")
    print("API/Web verification:      REAL APP")
    print("Schema migration:          NO")

    persisted = (
        container.investigation_persistence_service
        .persist_routing_decision(
            server_id=report.server_id,
            report_id=report.id,
            analysis_id=analysis.id,
            decision=decision,
            budget=budget,
            routing_version="acceptance-4.19.6-v2",
        )
    )

    persisted_id = persisted.investigation_id

    print()
    print("## PERSISTED INVESTIGATION")
    print()
    print(f"Investigation ID:          {persisted_id}")
    print(f"Initial status:            {persisted.status}")

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
        investigation_id=persisted_id,
    )

    executed = {
        run.specialist_slug
        for run in runtime_result.runs
    }

    if args.initial_specialist not in executed:
        raise RuntimeError(
            "Primary Specialist did not execute."
        )

    if args.secondary_specialist not in executed:
        raise RuntimeError(
            "Secondary Specialist did not execute "
            "through the real parallel coordinator."
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
            investigation_id=persisted_id,
            coordinator_result=controlled_result,
            final_diagnosis=diagnosis,
            narrative=narrative,
        )
    )

    print()
    print("## SNAPSHOT WRITE")
    print()
    print(
        f"Persisted status:          "
        f"{persisted_after_runtime.status}"
    )
    print(
        f"Runtime ID:                "
        f"{runtime_result.state.investigation_id}"
    )
    print(
        f"Specialist runs:           "
        f"{len(runtime_result.runs)}"
    )
    print(
        f"Evidence items:            "
        f"{len(runtime_result.state.evidence)}"
    )
    print(
        f"Claims:                    "
        f"{len(diagnosis.claims)}"
    )
    print(
        f"Conflicts:                 "
        f"{len(diagnosis.conflicts)}"
    )
    print(
        f"Narrative fallback:        "
        f"{narrative.used_fallback}"
    )

    checks: dict[str, bool] = {}

    client = TestClient(app)

    print()
    print("## API VERIFICATION")
    print()

    detail_response = client.get(
        f"/api/investigations/{persisted_id}"
    )

    record_check(
        checks,
        "api_detail_200",
        detail_response.status_code == 200,
        f"HTTP {detail_response.status_code}",
    )

    detail = (
        detail_response.json()
        if detail_response.status_code == 200
        else {}
    )

    record_check(
        checks,
        "persisted_identity_matches",
        detail.get("investigation_id") == persisted_id,
    )

    record_check(
        checks,
        "persisted_status_completed",
        detail.get("status") == "completed",
        str(detail.get("status")),
    )

    record_check(
        checks,
        "runtime_available_true",
        detail.get("runtime_available") is True,
    )

    record_check(
        checks,
        "final_diagnosis_available_true",
        detail.get("final_diagnosis_available") is True,
    )

    runtime = detail.get("runtime")

    record_check(
        checks,
        "runtime_object_present",
        isinstance(runtime, dict),
    )

    if isinstance(runtime, dict):
        specialist_runs = (
            runtime.get("specialist_runs")
            or []
        )
        evidence = (
            runtime.get("evidence")
            or []
        )
        claims = (
            runtime.get("correlated_claims")
            or []
        )
        conflicts = (
            runtime.get("conflicts")
            or []
        )
        final_diagnosis = runtime.get(
            "final_diagnosis"
        )
        persisted_narrative = runtime.get(
            "narrative"
        )

        record_check(
            checks,
            "two_specialist_runs_persisted",
            len(specialist_runs) >= 2,
            f"count={len(specialist_runs)}",
        )

        persisted_slugs = {
            item.get("specialist_slug")
            for item in specialist_runs
            if isinstance(item, dict)
        }

        record_check(
            checks,
            "expected_specialists_persisted",
            {
                args.initial_specialist,
                args.secondary_specialist,
            }
            <= persisted_slugs,
        )

        record_check(
            checks,
            "evidence_persisted",
            len(evidence) >= 1,
            f"count={len(evidence)}",
        )

        record_check(
            checks,
            "claims_persisted",
            len(claims) >= 1,
            f"count={len(claims)}",
        )

        record_check(
            checks,
            "conflicts_persisted",
            len(conflicts) >= 1,
            f"count={len(conflicts)}",
        )

        record_check(
            checks,
            "final_diagnosis_persisted",
            isinstance(
                final_diagnosis,
                dict,
            ),
        )

        record_check(
            checks,
            "narrative_persisted",
            isinstance(
                persisted_narrative,
                dict,
            ),
        )

        evidence_ids = {
            item.get("evidence_id")
            for item in evidence
            if isinstance(item, dict)
            and item.get("evidence_id")
        }

        claim_evidence_ids = {
            evidence_id
            for claim in claims
            if isinstance(claim, dict)
            for evidence_id in (
                claim.get("evidence_ids")
                or []
            )
        }

        conflict_evidence_ids = {
            evidence_id
            for conflict in conflicts
            if isinstance(conflict, dict)
            for evidence_id in (
                conflict.get("evidence_ids")
                or []
            )
        }

        record_check(
            checks,
            "claim_evidence_trace_valid",
            claim_evidence_ids <= evidence_ids,
        )

        record_check(
            checks,
            "conflict_evidence_trace_valid",
            conflict_evidence_ids <= evidence_ids,
        )

        expected_claim_ids = {
            claim.claim_id
            for claim in diagnosis.claims
        }

        expected_conflict_ids = {
            conflict.conflict_id
            for conflict in diagnosis.conflicts
        }

        persisted_claim_ids = {
            item.get("claim_id")
            for item in claims
            if isinstance(item, dict)
        }

        persisted_conflict_ids = {
            item.get("conflict_id")
            for item in conflicts
            if isinstance(item, dict)
        }

        record_check(
            checks,
            "claim_ids_preserved",
            expected_claim_ids
            == persisted_claim_ids,
        )

        record_check(
            checks,
            "conflict_ids_preserved",
            expected_conflict_ids
            == persisted_conflict_ids,
        )

        if isinstance(
            persisted_narrative,
            dict,
        ):
            narrative_claim_ids = set(
                persisted_narrative.get(
                    "claim_ids"
                )
                or []
            )

            narrative_conflict_ids = set(
                persisted_narrative.get(
                    "conflict_ids"
                )
                or []
            )

            record_check(
                checks,
                "narrative_claim_ids_valid",
                narrative_claim_ids
                <= expected_claim_ids,
            )

            record_check(
                checks,
                "narrative_conflicts_preserved",
                expected_conflict_ids
                <= narrative_conflict_ids,
            )
        else:
            record_check(
                checks,
                "narrative_claim_ids_valid",
                False,
            )

            record_check(
                checks,
                "narrative_conflicts_preserved",
                False,
            )
    else:
        for name in (
            "two_specialist_runs_persisted",
            "expected_specialists_persisted",
            "evidence_persisted",
            "claims_persisted",
            "conflicts_persisted",
            "final_diagnosis_persisted",
            "narrative_persisted",
            "claim_evidence_trace_valid",
            "conflict_evidence_trace_valid",
            "claim_ids_preserved",
            "conflict_ids_preserved",
            "narrative_claim_ids_valid",
            "narrative_conflicts_preserved",
        ):
            record_check(
                checks,
                name,
                False,
            )

    report_response = client.get(
        f"/api/reports/{report.id}/investigations"
    )

    record_check(
        checks,
        "report_api_200",
        report_response.status_code == 200,
        f"HTTP {report_response.status_code}",
    )

    report_rows = (
        report_response.json()
        if report_response.status_code == 200
        else []
    )

    record_check(
        checks,
        "report_api_contains_investigation",
        any(
            isinstance(item, dict)
            and item.get("investigation_id")
            == persisted_id
            for item in report_rows
        ),
    )

    list_response = client.get(
        "/api/investigations",
        params={"limit": 100},
    )

    record_check(
        checks,
        "list_api_200",
        list_response.status_code == 200,
        f"HTTP {list_response.status_code}",
    )

    list_rows = (
        list_response.json()
        if list_response.status_code == 200
        else []
    )

    record_check(
        checks,
        "list_api_runtime_flags_true",
        any(
            isinstance(item, dict)
            and item.get("investigation_id")
            == persisted_id
            and item.get("runtime_available")
            is True
            and item.get(
                "final_diagnosis_available"
            )
            is True
            for item in list_rows
        ),
    )

    print()
    print("## WEB VERIFICATION")
    print()

    web_list = client.get(
        "/investigations"
    )

    record_check(
        checks,
        "web_list_200",
        web_list.status_code == 200,
        f"HTTP {web_list.status_code}",
    )

    web_detail = client.get(
        f"/investigations/{persisted_id}"
    )

    record_check(
        checks,
        "web_detail_200",
        web_detail.status_code == 200,
        f"HTTP {web_detail.status_code}",
    )

    record_check(
        checks,
        "web_detail_contains_identity",
        persisted_id in web_detail.text,
    )

    record_check(
        checks,
        "global_action_budget_safe",
        runtime_result.investigation_actions_used
        <= budget.max_actions,
        (
            f"{runtime_result.investigation_actions_used}"
            f"/{budget.max_actions}"
        ),
    )

    print()
    print("## ACCEPTANCE RESULT")
    print()

    passed = all(checks.values())

    print(
        "Phase 4.19.6-v2: "
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

    print()
    print(
        f"Persisted acceptance Investigation: "
        f"{persisted_id}"
    )

    print(
        "NOTE: This record is retained as end-to-end "
        "persistence/API/UI acceptance evidence."
    )

    return 0 if passed else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 4.19.6-v2 persisted runtime snapshot acceptance."
        )
    )

    parser.add_argument(
        "report_id",
        nargs="?",
        type=int,
        default=1076,
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
