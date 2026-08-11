import pytest

from app.domain.investigation import (
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


def make_state(
    *,
    max_specialists: int = 4,
    max_rounds: int = 3,
) -> ServerInvestigationState:
    return ServerInvestigationState(
        investigation_id="inv-1",
        server_id=7,
        report_id=21,
        analysis_id=13,
        budget=InvestigationBudget(
            max_specialists=max_specialists,
            max_rounds=max_rounds,
            max_actions=12,
        ),
    )


def make_task(
    task_id: str,
    specialist_id: str,
    *,
    round_number: int = 1,
) -> SpecialistTask:
    return SpecialistTask(
        task_id=task_id,
        investigation_id="inv-1",
        server_id=7,
        report_id=21,
        specialist_id=specialist_id,
        objective="Investigate the detected anomaly.",
        round_number=round_number,
    )


def test_default_investigation_state() -> None:
    state = make_state()

    assert state.status == InvestigationStatus.CREATED
    assert state.round_number == 1
    assert state.tasks == []
    assert state.results == []


def test_confidence_must_be_normalized() -> None:
    with pytest.raises(ValueError):
        InvestigationFinding(
            finding_id="finding-1",
            title="High CPU",
            description="CPU is high.",
            confidence=1.1,
        )


def test_duplicate_evidence_is_rejected() -> None:
    state = make_state()

    evidence = EvidenceReference(
        evidence_id="ev-1",
        kind=EvidenceKind.MONITORING_REPORT,
        title="Monitoring report",
    )

    state.add_evidence(evidence)

    with pytest.raises(ValueError):
        state.add_evidence(evidence)


def test_task_must_belong_to_same_investigation() -> None:
    state = make_state()

    task = SpecialistTask(
        task_id="task-1",
        investigation_id="other",
        server_id=7,
        report_id=21,
        specialist_id="cpu",
        objective="Investigate CPU.",
    )

    with pytest.raises(ValueError):
        state.add_task(task)


def test_specialist_budget_counts_unique_specialists() -> None:
    state = make_state(
        max_specialists=2
    )

    state.add_task(
        make_task("task-1", "cpu")
    )
    state.add_task(
        make_task("task-2", "memory")
    )

    # A second task for an existing specialist is allowed.
    state.add_task(
        make_task("task-3", "cpu")
    )

    with pytest.raises(ValueError):
        state.add_task(
            make_task("task-4", "postgresql")
        )


def test_round_budget_is_enforced() -> None:
    state = make_state(
        max_rounds=2
    )

    with pytest.raises(ValueError):
        state.add_task(
            make_task(
                "task-1",
                "cpu",
                round_number=3,
            )
        )


def test_result_must_reference_existing_task() -> None:
    state = make_state()

    result = SpecialistResult(
        task_id="missing",
        specialist_id="cpu",
        status=SpecialistTaskStatus.COMPLETED,
        summary="Completed.",
        confidence=0.8,
    )

    with pytest.raises(ValueError):
        state.add_result(result)


def test_result_specialist_must_match_task() -> None:
    state = make_state()
    state.add_task(
        make_task("task-1", "cpu")
    )

    result = SpecialistResult(
        task_id="task-1",
        specialist_id="memory",
        status=SpecialistTaskStatus.COMPLETED,
        summary="Completed.",
        confidence=0.8,
    )

    with pytest.raises(ValueError):
        state.add_result(result)


def test_pending_result_is_invalid() -> None:
    with pytest.raises(ValueError):
        SpecialistResult(
            task_id="task-1",
            specialist_id="cpu",
            status=SpecialistTaskStatus.PENDING,
            summary="Not finished.",
            confidence=0.1,
        )


def test_valid_result_can_be_added() -> None:
    state = make_state()
    state.add_task(
        make_task("task-1", "cpu")
    )

    result = SpecialistResult(
        task_id="task-1",
        specialist_id="cpu",
        status=SpecialistTaskStatus.COMPLETED,
        summary="CPU load is caused by PID 4218.",
        confidence=0.93,
    )

    state.add_result(result)

    assert state.results == [result]
