"""Tests for test investigation contracts.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.investigation.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import pytest

from app.core.contracts.investigation.evidence_kind import EvidenceKind
from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.investigation_budget import InvestigationBudget
from app.core.contracts.investigation.investigation_finding import InvestigationFinding
from app.core.contracts.investigation.investigation_status import InvestigationStatus
from app.core.contracts.investigation.server_investigation_state import ServerInvestigationState
from app.core.contracts.investigation.specialist_result import SpecialistResult
from app.core.contracts.investigation.specialist_task import SpecialistTask
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus


def make_state(
    *,
    max_specialists: int = 4,
    max_rounds: int = 3,
) -> ServerInvestigationState:
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_state؛ المدخلات المهمة: max_specialists، max_rounds.
    تعيد ServerInvestigationState أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_task؛ المدخلات المهمة: task_id، specialist_id، round_number.
    تعيد SpecialistTask أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_default_investigation_state؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    state = make_state()

    assert state.status == InvestigationStatus.CREATED
    assert state.round_number == 1
    assert state.tasks == []
    assert state.results == []


def test_confidence_must_be_normalized() -> None:
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_confidence_must_be_normalized؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    with pytest.raises(ValueError):
        InvestigationFinding(
            finding_id="finding-1",
            title="High CPU",
            description="CPU is high.",
            confidence=1.1,
        )


def test_duplicate_evidence_is_rejected() -> None:
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_duplicate_evidence_is_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_task_must_belong_to_same_investigation؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_specialist_budget_counts_unique_specialists؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_round_budget_is_enforced؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_result_must_reference_existing_task؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_result_specialist_must_match_task؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_pending_result_is_invalid؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    with pytest.raises(ValueError):
        SpecialistResult(
            task_id="task-1",
            specialist_id="cpu",
            status=SpecialistTaskStatus.PENDING,
            summary="Not finished.",
            confidence=0.1,
        )


def test_valid_result_can_be_added() -> None:
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_valid_result_can_be_added؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
