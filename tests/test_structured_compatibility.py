"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.structured_compatibility.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import json

from app.capabilities.analysis.retrieval.structured_compatibility import (
    StructuredCompatibilityChecker,
)


def report(
    *,
    connection_successful=True,
    success=True,
    exit_status=0,
    error_message="",
    stderr="",
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى report؛ المدخلات المهمة: connection_successful، success، exit_status، error_message، stderr.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return json.dumps(
        {
            "connection_successful": connection_successful,
            "error_message": error_message,
            "executions": [
                {
                    "command_id": 10,
                    "success": success,
                    "exit_status": exit_status,
                    "error_message": "",
                    "stderr": stderr,
                }
            ],
        },
        sort_keys=True,
    )


def test_identical_structured_state_is_compatible():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_identical_structured_state_is_compatible؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    checker = StructuredCompatibilityChecker()

    result = checker.check(
        current_normalized_report=report(),
        historical_normalized_report=report(),
    )

    assert result.compatible is True
    assert result.conflicts == []


def test_connection_state_conflict_is_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_connection_state_conflict_is_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    checker = StructuredCompatibilityChecker()

    result = checker.check(
        current_normalized_report=report(
            connection_successful=True,
        ),
        historical_normalized_report=report(
            connection_successful=False,
        ),
    )

    assert result.compatible is False
    assert any(
        conflict.field == "connection_successful"
        for conflict in result.conflicts
    )


def test_command_success_conflict_is_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_command_success_conflict_is_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    checker = StructuredCompatibilityChecker()

    result = checker.check(
        current_normalized_report=report(success=True),
        historical_normalized_report=report(success=False),
    )

    assert result.compatible is False
    assert any(
        conflict.field == "success"
        and conflict.command_id == 10
        for conflict in result.conflicts
    )


def test_exit_status_class_conflict_is_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_exit_status_class_conflict_is_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    checker = StructuredCompatibilityChecker()

    result = checker.check(
        current_normalized_report=report(exit_status=0),
        historical_normalized_report=report(exit_status=2),
    )

    assert result.compatible is False
    assert any(
        conflict.field == "exit_status_class"
        for conflict in result.conflicts
    )


def test_disjoint_error_signatures_are_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_disjoint_error_signatures_are_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    checker = StructuredCompatibilityChecker()

    result = checker.check(
        current_normalized_report=report(
            error_message="connection refused",
        ),
        historical_normalized_report=report(
            error_message="permission denied",
        ),
    )

    assert result.compatible is False
    assert any(
        conflict.field == "error_signatures"
        for conflict in result.conflicts
    )


def test_invalid_normalized_report_is_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_invalid_normalized_report_is_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    checker = StructuredCompatibilityChecker()

    result = checker.check(
        current_normalized_report="{invalid",
        historical_normalized_report=report(),
    )

    assert result.compatible is False
    assert result.conflicts[0].field == "normalized_report"
