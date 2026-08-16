"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.contracts.investigation، app.capabilities.investigation.correlation، app.capabilities.investigation.execution_contracts.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
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
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_state؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    state = ServerInvestigationState(
        investigation_id="inv-1",
        server_id=2,
        report_id=10,
        analysis_id=20,
        status=InvestigationStatus.COMPLETED,
        budget=InvestigationBudget(),
    )
    state.add_evidence(
        EvidenceReference(
            evidence_id="e1",
            kind=EvidenceKind.COMMAND_RESULT,
            title="service status",
        )
    )
    state.add_evidence(
        EvidenceReference(
            evidence_id="e2",
            kind=EvidenceKind.COMMAND_RESULT,
            title="listener status",
        )
    )
    return state


def make_run(*, slug, finding):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_run؛ المدخلات المهمة: slug، finding.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    task = SpecialistTask(
        task_id=f"inv-1:{slug}:1",
        investigation_id="inv-1",
        server_id=2,
        report_id=10,
        specialist_id=slug,
        objective="Diagnose.",
        status=SpecialistTaskStatus.RUNNING,
    )
    result = SpecialistResult(
        task_id=task.task_id,
        specialist_id=slug,
        status=SpecialistTaskStatus.COMPLETED,
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
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى wrap؛ المدخلات المهمة: state.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    for run in runs:
        state.add_task(run.task)
        state.add_result(run.result)
    return InvestigationExecutionResult(
        state=state,
        runs=tuple(runs),
        investigation_actions_used=1,
    )


def test_live_evidence_high_confidence_is_confirmed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_live_evidence_high_confidence_is_confirmed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    state = make_state()
    run = make_run(
        slug="nginx",
        finding=InvestigationFinding(
            finding_id="f1",
            title="NGINX service absent",
            description="nginx.service was not found.",
            confidence=0.95,
            evidence_ids=("e1",),
        ),
    )

    output = CrossSpecialistCorrelator().correlate(
        wrap(state, run)
    )

    assert output.confirmed_count == 1
    assert output.claims[0].certainty == (
        DiagnosisCertainty.CONFIRMED
    )


def test_live_evidence_lower_confidence_is_probable():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_live_evidence_lower_confidence_is_probable؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    state = make_state()
    run = make_run(
        slug="linux-network",
        finding=InvestigationFinding(
            finding_id="f2",
            title="Network path degraded",
            description="Connectivity appears degraded.",
            confidence=0.65,
            evidence_ids=("e2",),
        ),
    )

    output = CrossSpecialistCorrelator().correlate(
        wrap(state, run)
    )

    assert output.probable_count == 1
    assert output.claims[0].certainty == (
        DiagnosisCertainty.PROBABLE
    )


def test_knowledge_only_finding_remains_unknown():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_knowledge_only_finding_remains_unknown؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    state = make_state()
    run = make_run(
        slug="nginx",
        finding=InvestigationFinding(
            finding_id="f3",
            title="NGINX proxy behavior",
            description="Documentation describes proxying.",
            confidence=0.99,
            knowledge_source_ids=(
                "knowledge-chunk:12",
            ),
        ),
    )

    output = CrossSpecialistCorrelator().correlate(
        wrap(state, run)
    )

    assert output.unknown_count == 1
    assert output.claims[0].certainty == (
        DiagnosisCertainty.UNKNOWN
    )


def test_same_title_merges_specialists():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_same_title_merges_specialists؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    state = make_state()

    run1 = make_run(
        slug="nginx",
        finding=InvestigationFinding(
            finding_id="f4",
            title="NGINX service absent",
            description="Service unit absent.",
            confidence=0.95,
            evidence_ids=("e1",),
        ),
    )
    run2 = make_run(
        slug="systemd-service",
        finding=InvestigationFinding(
            finding_id="f5",
            title="NGINX service absent",
            description="systemd has no nginx.service.",
            confidence=0.90,
            evidence_ids=("e1",),
        ),
    )

    output = CrossSpecialistCorrelator().correlate(
        wrap(state, run1, run2)
    )

    assert len(output.claims) == 1
    assert output.claims[0].specialist_slugs == (
        "nginx",
        "systemd-service",
    )


def test_unknown_evidence_reference_fails_closed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_unknown_evidence_reference_fails_closed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    state = make_state()
    run = make_run(
        slug="nginx",
        finding=InvestigationFinding(
            finding_id="f6",
            title="Unknown provenance",
            description="Bad evidence reference.",
            confidence=0.9,
            evidence_ids=("invented-evidence",),
        ),
    )

    try:
        CrossSpecialistCorrelator().correlate(
            wrap(state, run)
        )
    except ValueError as exc:
        assert "unknown evidence IDs" in str(exc)
    else:
        raise AssertionError(
            "Unknown Evidence IDs must fail closed."
        )
