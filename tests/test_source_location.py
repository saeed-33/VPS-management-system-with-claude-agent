from types import SimpleNamespace

from app.capabilities.investigation.correlation import CrossSpecialistCorrelator
from app.capabilities.investigation.correlation import FinalDiagnosis
from app.capabilities.investigation.source_location import extract_source_locations
from app.capabilities.investigation.specialist_reasoning_agent import SpecialistReasoningAgent
from app.capabilities.investigation.runtime_snapshot_service import InvestigationRuntimeSnapshotService
from app.core.contracts.investigation import EvidenceKind, EvidenceReference
from app.core.contracts.specialist_reasoning import SpecialistFindingOutput, SpecialistReasoningOutput
from app.interfaces.admin.schemas.investigations import InvestigationRuntimeResponse


def test_python_traceback_location_contains_reason_and_evidence_binding():
    locations = extract_source_locations(
        'Traceback (most recent call last):\n'
        '  File "/srv/app/main.py", line 42, in start_service\n'
        '    raise TypeError("bad state")\n'
        'TypeError: bad state\n',
        evidence_ids=("evidence-1",),
    )

    assert len(locations) == 1
    location = locations[0]
    assert location.file_path == "/srv/app/main.py"
    assert location.line_number == 42
    assert location.function == "start_service"
    assert location.exception_type == "TypeError"
    assert location.reason == "TypeError: bad state"
    assert location.source == "python_traceback"
    assert location.evidence_ids == ("evidence-1",)


def test_generic_source_location_supports_column_and_rejects_transport_errors():
    locations = extract_source_locations("build failed at /srv/app/index.ts:10:4")
    assert locations[0].file_path == "/srv/app/index.ts"
    assert locations[0].line_number == 10
    assert locations[0].column_number == 4
    assert extract_source_locations("src/module.py:17")[0].line_number == 17
    assert extract_source_locations("ssh: connect to host x port 22: Connection refused") == ()
    assert extract_source_locations("request finished in 42ms") == ()


def test_specialist_location_metadata_can_only_come_from_referenced_evidence():
    evidence = EvidenceReference(
        evidence_id="e1",
        kind=EvidenceKind.COMMAND_RESULT,
        title="Diagnostic output",
        excerpt="File \"/srv/app/main.py\", line 8, in run\nValueError: bad",
        metadata={},
    )
    context = SimpleNamespace(
        task_id="task-1",
        specialist_slug="systemd-service",
        character_count=10,
        evidence=(evidence,),
    )
    output = SpecialistReasoningOutput(
        summary="failure",
        confidence=0.9,
        findings=[
            SpecialistFindingOutput(
                title="Service error",
                description="The service raised an application error.",
                confidence=0.9,
                evidence_ids=["e1"],
            )
        ],
    )

    result = SpecialistReasoningAgent._to_result(output=output, context=context)
    locations = result.findings[0].metadata["code_locations"]
    assert locations[0]["file_path"] == "/srv/app/main.py"
    assert locations[0]["evidence_ids"] == ["e1"]


def test_correlator_carries_finding_locations_into_claim_metadata():
    finding = SimpleNamespace(
        finding_id="f1",
        title="Application failure",
        description="A source error was observed.",
        confidence=0.9,
        evidence_ids=("e1",),
        knowledge_source_ids=(),
        missing_evidence=(),
        metadata={
            "code_locations": [{
                "file_path": "/srv/app/main.py",
                "line_number": 8,
                "evidence_ids": ["e1"],
            }]
        },
    )
    claim, _ = CrossSpecialistCorrelator()._build_claim(
        investigation_id="inv-1",
        index=1,
        correlation_key="application failure",
        items=[("systemd-service", finding)],
    )
    assert claim.metadata["code_locations"][0]["line_number"] == 8


def test_traceback_evidence_reaches_persisted_projection_and_api_read_model():
    evidence = EvidenceReference(
        evidence_id="e2",
        kind=EvidenceKind.COMMAND_RESULT,
        title="Application traceback",
        excerpt='File "/app/service.py", line 42, in handle\nValueError: invalid payload',
    )
    context = SimpleNamespace(
        task_id="task-2",
        specialist_slug="systemd-service",
        character_count=10,
        evidence=(evidence,),
    )
    reasoning = SpecialistReasoningOutput(
        summary="Application error located.",
        confidence=0.9,
        findings=[
            SpecialistFindingOutput(
                title="Application exception",
                description="The application raised a ValueError.",
                confidence=0.9,
                evidence_ids=["e2"],
            )
        ],
    )
    specialist_result = SpecialistReasoningAgent._to_result(
        output=reasoning,
        context=context,
    )
    finding = specialist_result.findings[0]
    claim, _ = CrossSpecialistCorrelator()._build_claim(
        investigation_id="inv-2",
        index=1,
        correlation_key="application exception",
        items=[("systemd-service", finding)],
    )
    diagnosis = FinalDiagnosis(
        investigation_id="inv-2",
        summary="Application exception located.",
        claims=(claim,),
        conflicts=(),
        confirmed_count=1,
        probable_count=0,
        unknown_count=0,
        conflict_count=0,
        evidence_ids=("e2",),
        specialist_slugs=("systemd-service",),
        metadata={"code_locations": claim.metadata["code_locations"]},
    )

    projection_service = InvestigationRuntimeSnapshotService(SimpleNamespace())
    runtime = {
        "correlated_claims": (projection_service._serialize_claim(claim),),
        "final_diagnosis": projection_service._serialize_final_diagnosis(diagnosis),
    }
    read_model = InvestigationRuntimeResponse.model_validate(runtime)
    location = read_model.correlated_claims[0]["metadata"]["code_locations"][0]
    assert location["file_path"] == "/app/service.py"
    assert location["line_number"] == 42
    assert location["reason"] == "ValueError: invalid payload"
    assert location["evidence_ids"] == ["e2"]
