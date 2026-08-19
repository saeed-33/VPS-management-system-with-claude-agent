"""Tests for test dataset runner.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from tools.acceptance.evaluation.runner import DeterministicEvaluationRunner, EvaluationCaseResult, expected_behavior_executor
from tools.acceptance.evaluation.contracts import EvaluationMetric, ReadinessStatus
from tools.acceptance.evaluation.cases import default_evaluation_cases


def test_default_dataset_meets_gate_sample_counts():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_default_dataset_meets_gate_sample_counts؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    cases = default_evaluation_cases()

    counts = {}

    for case in cases:
        for metric in case.expected_metrics:
            counts[metric] = (
                counts.get(metric, 0) + 1
            )

    assert (
        counts[
            EvaluationMetric.ROUTING_RECALL
        ]
        >= 10
    )

    assert (
        counts[
            EvaluationMetric
            .SPECIALIST_COMPLETION
        ]
        >= 10
    )

    assert (
        counts[
            EvaluationMetric
            .EVIDENCE_GROUNDING
        ]
        >= 10
    )

    assert (
        counts[
            EvaluationMetric
            .BUDGET_COMPLIANCE
        ]
        >= 10
    )

    assert (
        counts[
            EvaluationMetric
            .CONFLICT_PRESERVATION
        ]
        >= 5
    )

    assert (
        counts[
            EvaluationMetric
            .FINAL_DIAGNOSIS_GROUNDING
        ]
        >= 10
    )

    assert (
        counts[
            EvaluationMetric
            .PROVIDER_RESILIENCE
        ]
        >= 10
    )

    assert (
        counts[
            EvaluationMetric.POLICY_SAFETY
        ]
        >= 10
    )


def test_case_ids_are_unique():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_case_ids_are_unique؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    cases = default_evaluation_cases()

    ids = [
        case.case_id
        for case in cases
    ]

    assert len(ids) == len(set(ids))


def test_expected_behavior_executor_wires_gate():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_expected_behavior_executor_wires_gate؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = (
        DeterministicEvaluationRunner()
        .run(
            cases=(
                default_evaluation_cases()
            ),
            executor=(
                expected_behavior_executor
            ),
        )
    )

    assert (
        result.cases_total
        == len(
            default_evaluation_cases()
        )
    )

    assert (
        result.cases_passed
        == result.cases_total
    )

    assert (
        result.readiness.status
        == ReadinessStatus
        .READY_FOR_SUPERVISED_OPERATIONS
    )

    assert (
        result.readiness
        .automatic_remediation_allowed
        is False
    )


def test_runtime_failure_blocks_hard_metric():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_failure_blocks_hard_metric؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    cases = default_evaluation_cases()

    def executor(case):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى executor؛ المدخلات المهمة: case.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        if (
            EvaluationMetric
            .EVIDENCE_GROUNDING
            in case.expected_metrics
            and case.case_id
            == "evidence-grounding-01"
        ):
            return EvaluationCaseResult(
                case_id=case.case_id,
                passed=False,
                score=0.0,
                details=(
                    "Injected unknown Evidence ID."
                ),
            )

        return EvaluationCaseResult(
            case_id=case.case_id,
            passed=True,
            score=1.0,
        )

    result = (
        DeterministicEvaluationRunner()
        .run(
            cases=cases,
            executor=executor,
        )
    )

    assert (
        result.readiness.status
        == ReadinessStatus.BLOCKED
    )

    assert any(
        "evidence_grounding"
        in reason
        for reason in (
            result.readiness
            .blocking_reasons
        )
    )


def test_executor_must_return_matching_case_id():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_executor_must_return_matching_case_id؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    case = default_evaluation_cases()[0]

    def bad_executor(_):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى bad_executor؛ المدخلات المهمة: _.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return EvaluationCaseResult(
            case_id="wrong",
            passed=True,
        )

    try:
        DeterministicEvaluationRunner().run(
            cases=(case,),
            executor=bad_executor,
        )
    except ValueError as exc:
        assert (
            "wrong case_id"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Wrong case_id accepted."
        )


def test_duplicate_case_ids_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_duplicate_case_ids_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    case = default_evaluation_cases()[0]

    try:
        DeterministicEvaluationRunner().run(
            cases=(
                case,
                case,
            ),
            executor=(
                expected_behavior_executor
            ),
        )
    except ValueError as exc:
        assert (
            "Duplicate EvaluationCase IDs"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Duplicate cases accepted."
        )
