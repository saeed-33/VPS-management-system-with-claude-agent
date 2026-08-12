from types import SimpleNamespace

from app.domain.investigation.contracts import (
    EvidenceKind,
    EvidenceReference,
    InvestigationBudget,
    InvestigationStatus,
    ServerInvestigationState,
    SpecialistResult,
    SpecialistTask,
    SpecialistTaskStatus,
)
from app.domain.investigation.correlation import (
    CorrelatedDiagnosisClaim,
    DiagnosisCertainty,
    DiagnosisConflict,
    FinalDiagnosis,
)
from app.domain.investigation.final_diagnosis_synthesizer import (
    FinalDiagnosisNarrative,
)
from app.domain.investigation.runtime_snapshot_service import (
    InvestigationRuntimeSnapshotService,
)
from app.domain.investigation.execution_contracts import (
    InvestigationExecutionResult,
    InvestigationSpecialistRun,
)


class Repository:
    def __init__(self):
        self.model = SimpleNamespace(
            investigation_id="persisted-1",
            status="created",
            investigation_metadata={
                "routing": "kept"
            },
        )
        self.updated = None

    def get_by_investigation_id(
        self,
        investigation_id,
    ):
        if investigation_id == "persisted-1":
            return self.model
        return None

    def update_runtime_snapshot(
        self,
        *,
        investigation_id,
        status,
        metadata,
    ):
        self.updated = {
            "investigation_id": (
                investigation_id
            ),
            "status": status,
            "metadata": metadata,
        }
        return self.updated


def make_result():
    state = ServerInvestigationState(
        investigation_id="runtime-1",
        server_id=2,
        report_id=10,
        analysis_id=20,
        status=(
            InvestigationStatus.COMPLETED
        ),
        budget=InvestigationBudget(
            max_specialists=2,
            max_rounds=3,
            max_actions=10,
        ),
        metadata={
            "orchestrator": "claude",
            "execution_mode": (
                "dynamic-secondary"
            ),
            "waves_completed": 2,
            "executed_specialists": [
                "nginx",
            ],
        },
    )

    state.add_evidence(
        EvidenceReference(
            evidence_id="e1",
            kind=(
                EvidenceKind.COMMAND_RESULT
            ),
            title="status",
            source_id="runtime",
            excerpt="ok",
        )
    )

    task = SpecialistTask(
        task_id="runtime-1:nginx:1",
        investigation_id="runtime-1",
        server_id=2,
        report_id=10,
        specialist_id="nginx",
        objective="Diagnose.",
        status=(
            SpecialistTaskStatus.RUNNING
        ),
    )

    result = SpecialistResult(
        task_id=task.task_id,
        specialist_id="nginx",
        status=(
            SpecialistTaskStatus.COMPLETED
        ),
        summary="Done.",
        confidence=0.9,
        evidence_ids=("e1",),
    )

    run = InvestigationSpecialistRun(
        specialist_slug="nginx",
        task=task,
        result=result,
        loop_result=None,
    )

    return InvestigationExecutionResult(
        state=state,
        runs=(run,),
        investigation_actions_used=1,
    )


def make_diagnosis():
    claim = CorrelatedDiagnosisClaim(
        claim_id="runtime-1:claim:1",
        title="Service state",
        description="Known.",
        certainty=(
            DiagnosisCertainty.CONFIRMED
        ),
        confidence=0.9,
        specialist_slugs=("nginx",),
        evidence_ids=("e1",),
    )

    return FinalDiagnosis(
        investigation_id="runtime-1",
        summary="Confirmed.",
        claims=(claim,),
        conflicts=(),
        confirmed_count=1,
        probable_count=0,
        unknown_count=0,
        conflict_count=0,
        evidence_ids=("e1",),
        specialist_slugs=("nginx",),
        metadata={},
    )


def test_build_snapshot_serializes_runtime():
    service = (
        InvestigationRuntimeSnapshotService(
            Repository()
        )
    )

    snapshot = service.build_snapshot(
        execution_result=make_result(),
        final_diagnosis=make_diagnosis(),
    )

    assert snapshot["status"] == "completed"
    assert (
        snapshot["orchestrator"]
        == "claude"
    )
    assert snapshot["actions_used"] == 1
    assert snapshot["evidence_count"] == 1
    assert (
        snapshot["specialist_runs"][0][
            "specialist_slug"
        ]
        == "nginx"
    )
    assert (
        snapshot["correlated_claims"][0][
            "certainty"
        ]
        == "confirmed"
    )


def test_persist_preserves_existing_metadata():
    repository = Repository()
    service = (
        InvestigationRuntimeSnapshotService(
            repository
        )
    )

    result = service.persist(
        investigation_id="persisted-1",
        execution_result=make_result(),
        final_diagnosis=make_diagnosis(),
    )

    assert result["status"] == "completed"
    assert (
        result["metadata"]["routing"]
        == "kept"
    )
    assert (
        "runtime_snapshot"
        in result["metadata"]
    )
    assert (
        result["metadata"][
            "runtime_investigation_id"
        ]
        == "runtime-1"
    )


def test_narrative_is_persisted():
    service = (
        InvestigationRuntimeSnapshotService(
            Repository()
        )
    )

    narrative = FinalDiagnosisNarrative(
        summary="Operator summary.",
        claim_ids=(
            "runtime-1:claim:1",
        ),
        conflict_ids=(),
        operator_notes=("note",),
        provider_name="ollama",
        model_name="model",
        used_fallback=False,
        metadata={},
    )

    snapshot = service.build_snapshot(
        execution_result=make_result(),
        final_diagnosis=make_diagnosis(),
        narrative=narrative,
    )

    assert (
        snapshot["narrative"][
            "provider_name"
        ]
        == "ollama"
    )
    assert (
        snapshot["narrative"][
            "used_fallback"
        ]
        is False
    )


def test_missing_investigation_fails():
    service = (
        InvestigationRuntimeSnapshotService(
            Repository()
        )
    )

    try:
        service.persist(
            investigation_id="missing",
            execution_result=make_result(),
        )
    except ValueError as exc:
        assert (
            "Investigation not found"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Missing Investigation accepted."
        )
