from app.core.contracts.investigation import (
    EvidenceKind,
    EvidenceReference,
    InvestigationBudget,
    InvestigationFinding,
    InvestigationStatus,
    ServerInvestigationState,
    SpecialistResult,
    SpecialistTask,
    SpecialistTaskStatus,
)
from app.capabilities.investigation.correlation import (
    CrossSpecialistCorrelator,
    DiagnosisCertainty,
)
from app.capabilities.investigation.execution_contracts import (
    InvestigationExecutionResult,
    InvestigationSpecialistRun,
)


def make_state():
    state = ServerInvestigationState(
        investigation_id="inv-1",
        server_id=2,
        report_id=10,
        analysis_id=20,
        status=InvestigationStatus.COMPLETED,
        budget=InvestigationBudget(),
    )

    for evidence_id in ("e1", "e2"):
        state.add_evidence(
            EvidenceReference(
                evidence_id=evidence_id,
                kind=(
                    EvidenceKind
                    .COMMAND_RESULT
                ),
                title=evidence_id,
            )
        )

    return state


def make_run(
    *,
    slug,
    finding,
):
    task = SpecialistTask(
        task_id=f"inv-1:{slug}:1",
        investigation_id="inv-1",
        server_id=2,
        report_id=10,
        specialist_id=slug,
        objective="Diagnose.",
        status=(
            SpecialistTaskStatus.RUNNING
        ),
    )

    result = SpecialistResult(
        task_id=task.task_id,
        specialist_id=slug,
        status=(
            SpecialistTaskStatus.COMPLETED
        ),
        summary="Completed.",
        confidence=finding.confidence,
        findings=(finding,),
    )

    return InvestigationSpecialistRun(
        specialist_slug=slug,
        task=task,
        result=result,
        loop_result=None,
    )


def wrap(state, *runs):
    for run in runs:
        state.add_task(run.task)
        state.add_result(run.result)

    return InvestigationExecutionResult(
        state=state,
        runs=tuple(runs),
        investigation_actions_used=1,
    )


def test_explicit_conflicting_states_become_unknown():
    state = make_state()

    run1 = make_run(
        slug="nginx",
        finding=InvestigationFinding(
            finding_id="f1",
            title="NGINX service presence",
            description=(
                "NGINX service appears absent."
            ),
            confidence=0.95,
            evidence_ids=("e1",),
            metadata={
                "diagnostic_state": "absent"
            },
        ),
    )

    run2 = make_run(
        slug="systemd-service",
        finding=InvestigationFinding(
            finding_id="f2",
            title="NGINX service presence",
            description=(
                "NGINX service appears present."
            ),
            confidence=0.90,
            evidence_ids=("e2",),
            metadata={
                "diagnostic_state": "present"
            },
        ),
    )

    output = (
        CrossSpecialistCorrelator()
        .correlate(
            wrap(
                state,
                run1,
                run2,
            )
        )
    )

    assert len(output.claims) == 1
    assert output.conflict_count == 1
    assert output.unknown_count == 1
    assert (
        output.claims[0].certainty
        == DiagnosisCertainty.UNKNOWN
    )
    assert (
        output.claims[0]
        .metadata["conflict"]
        is True
    )
    assert set(
        output.conflicts[0]
        .diagnostic_states
    ) == {
        "absent",
        "present",
    }


def test_matching_explicit_states_do_not_conflict():
    state = make_state()

    run1 = make_run(
        slug="nginx",
        finding=InvestigationFinding(
            finding_id="f3",
            title="NGINX service presence",
            description="Service absent.",
            confidence=0.95,
            evidence_ids=("e1",),
            metadata={
                "diagnostic_state": "absent"
            },
        ),
    )

    run2 = make_run(
        slug="systemd-service",
        finding=InvestigationFinding(
            finding_id="f4",
            title="NGINX service presence",
            description="Unit absent.",
            confidence=0.92,
            evidence_ids=("e2",),
            metadata={
                "diagnostic_state": "absent"
            },
        ),
    )

    output = (
        CrossSpecialistCorrelator()
        .correlate(
            wrap(
                state,
                run1,
                run2,
            )
        )
    )

    assert output.conflict_count == 0
    assert output.confirmed_count == 1
    assert (
        output.claims[0].certainty
        == DiagnosisCertainty.CONFIRMED
    )


def test_no_state_metadata_keeps_original_certainty_rules():
    state = make_state()

    run = make_run(
        slug="linux-network",
        finding=InvestigationFinding(
            finding_id="f5",
            title="Network path degraded",
            description="Degraded.",
            confidence=0.65,
            evidence_ids=("e1",),
        ),
    )

    output = (
        CrossSpecialistCorrelator()
        .correlate(
            wrap(
                state,
                run,
            )
        )
    )

    assert output.conflict_count == 0
    assert output.probable_count == 1
