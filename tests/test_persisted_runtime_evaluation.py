from datetime import (
    datetime,
    timezone,
)

from tools.acceptance.evaluation import (
    EvaluationMetric,
)
from tools.acceptance.evaluation.persisted_runtime import (
    PersistedRuntimeEvaluator,
)
from app.core.contracts.investigation_read_models import (
    InvestigationCandidateReadModel,
    InvestigationDetailReadModel,
    InvestigationRuntimeReadModel,
)


NOW = datetime(
    2026,
    8,
    10,
    tzinfo=timezone.utc,
)


def make_detail(
    *,
    bad_evidence=False,
    bad_budget=False,
    bad_narrative=False,
    malformed_evidence=False,
    foreign_evidence=False,
    foreign_server=False,
):
    evidence_id = "e1"

    run_evidence_id = (
        "missing"
        if bad_evidence
        else evidence_id
    )

    run_evidence_ids = (
        [None]
        if malformed_evidence
        else [run_evidence_id]
    )

    evidence_metadata = {}
    if foreign_evidence:
        evidence_metadata["investigation_id"] = "other-investigation"
    if foreign_server:
        evidence_metadata["server_id"] = 99

    narrative_claim_ids = (
        ["unknown"]
        if bad_narrative
        else ["c1"]
    )

    runtime = (
        InvestigationRuntimeReadModel(
            status="completed",
            orchestrator="claude",
            execution_mode="parallel",
            waves_completed=1,
            actions_used=(
                11
                if bad_budget
                else 4
            ),
            evidence_count=1,
            specialist_runs=(
                {
                    "specialist_slug": (
                        "nginx"
                    ),
                    "status": "completed",
                    "evidence_ids": [
                        *run_evidence_ids
                    ],
                },
            ),
            evidence=(
                {
                    "evidence_id": evidence_id,
                    "metadata": evidence_metadata,
                },
            ),
            correlated_claims=(
                {
                    "claim_id": "c1",
                    "evidence_ids": [
                        evidence_id
                    ],
                },
            ),
            conflicts=(
                {
                    "conflict_id": "x1",
                    "evidence_ids": [
                        evidence_id
                    ],
                },
            ),
            final_diagnosis={
                "conflict_count": 1,
                "evidence_ids": [
                    evidence_id
                ],
            },
            narrative={
                "claim_ids": (
                    narrative_claim_ids
                ),
                "conflict_ids": ["x1"],
            },
        )
    )

    return InvestigationDetailReadModel(
        investigation_id="inv-1",
        server_id=2,
        report_id=1076,
        analysis_id=907,
        status="completed",
        should_investigate=True,
        routing_reasons=(),
        detected_domains=("nginx",),
        unmatched_issue_indexes=(),
        registry_size=1,
        candidate_limit=1,
        selection_limit=1,
        max_specialists=2,
        max_rounds=3,
        max_actions=10,
        routing_version="test",
        candidates=(
            InvestigationCandidateReadModel(
                specialist_definition_id=1,
                specialist_slug="nginx",
                specialist_name="NGINX",
                score=1,
                priority=1,
                candidate_rank=1,
                is_selected=True,
                selected_rank=1,
            ),
        ),
        runtime_available=True,
        final_diagnosis_available=True,
        runtime=runtime,
        metadata={},
        created_at=NOW,
        updated_at=NOW,
    )


def by_metric(result):
    return {
        item.metric: item
        for item in result.observations
    }


def test_valid_snapshot_emits_five_real_metrics():
    result = (
        PersistedRuntimeEvaluator()
        .evaluate(
            make_detail()
        )
    )

    assert len(
        result.observations
    ) == 5

    assert all(
        item.passed
        for item
        in result.observations
    )


def test_unknown_evidence_fails_grounding():
    result = (
        PersistedRuntimeEvaluator()
        .evaluate(
            make_detail(
                bad_evidence=True
            )
        )
    )

    metrics = by_metric(result)

    assert (
        metrics[
            EvaluationMetric
            .EVIDENCE_GROUNDING
        ].passed
        is False
    )


def test_budget_overrun_fails():
    result = (
        PersistedRuntimeEvaluator()
        .evaluate(
            make_detail(
                bad_budget=True
            )
        )
    )

    metrics = by_metric(result)

    assert (
        metrics[
            EvaluationMetric
            .BUDGET_COMPLIANCE
        ].passed
        is False
    )


def test_unknown_narrative_claim_fails():
    result = (
        PersistedRuntimeEvaluator()
        .evaluate(
            make_detail(
                bad_narrative=True
            )
        )
    )

    metrics = by_metric(result)

    assert (
        metrics[
            EvaluationMetric
            .FINAL_DIAGNOSIS_GROUNDING
        ].passed
        is False
    )


def test_malformed_evidence_reference_fails_closed():
    metrics = by_metric(
        PersistedRuntimeEvaluator().evaluate(
            make_detail(malformed_evidence=True)
        )
    )

    assert metrics[EvaluationMetric.EVIDENCE_GROUNDING].passed is False


def test_foreign_investigation_evidence_fails_closed():
    metrics = by_metric(
        PersistedRuntimeEvaluator().evaluate(
            make_detail(foreign_evidence=True)
        )
    )

    assert metrics[EvaluationMetric.EVIDENCE_GROUNDING].passed is False


def test_foreign_server_evidence_fails_closed():
    metrics = by_metric(
        PersistedRuntimeEvaluator().evaluate(
            make_detail(foreign_server=True)
        )
    )

    assert metrics[EvaluationMetric.EVIDENCE_GROUNDING].passed is False
