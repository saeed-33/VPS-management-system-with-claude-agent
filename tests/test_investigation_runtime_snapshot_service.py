"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.contracts.investigation، app.capabilities.investigation.correlation، app.capabilities.investigation.final_diagnosis_synthesizer، app.capabilities.investigation.runtime_snapshot_service، app.capabilities.investigation.execution_contracts.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from types import SimpleNamespace

from app.core.contracts.investigation import (
    EvidenceKind,
    EvidenceReference,
    InvestigationBudget,
    InvestigationStatus,
    ServerInvestigationState,
    SpecialistResult,
    SpecialistTask,
    SpecialistTaskStatus,
)
from app.capabilities.investigation.correlation import (
    CorrelatedDiagnosisClaim,
    DiagnosisCertainty,
    DiagnosisConflict,
    FinalDiagnosis,
)
from app.capabilities.investigation.final_diagnosis_synthesizer import (
    FinalDiagnosisNarrative,
)
from app.capabilities.investigation.runtime_snapshot_service import (
    InvestigationRuntimeSnapshotService,
)
from app.capabilities.investigation.execution_contracts import (
    InvestigationExecutionResult,
    InvestigationSpecialistRun,
)


class Repository:
    """
    يمثل Repository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
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
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_by_investigation_id؛ المدخلات المهمة: investigation_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
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
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى update_runtime_snapshot؛ المدخلات المهمة: investigation_id، status، metadata.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.updated = {
            "investigation_id": (
                investigation_id
            ),
            "status": status,
            "metadata": metadata,
        }
        return self.updated


def make_result():
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_result؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_diagnosis؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
        metadata={
            "code_locations": [{
                "file_path": "/srv/app/main.py",
                "line_number": 42,
                "reason": "ValueError: invalid payload",
                "source": "python_traceback",
                "evidence_ids": ["e1"],
            }],
        },
    )


def test_build_snapshot_serializes_runtime():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_build_snapshot_serializes_runtime؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    assert snapshot["final_diagnosis"]["metadata"]["code_locations"][0]["evidence_ids"] == ["e1"]


def test_persist_preserves_existing_metadata():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_persist_preserves_existing_metadata؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_narrative_is_persisted؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_missing_investigation_fails؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
