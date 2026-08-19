"""Tests for test runtime adapter.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.runtime.claude، app.runtime.claude.exceptions.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio
import json

from app.runtime.claude.models.job_status import ClaudeJobStatus
from app.runtime.claude.models.raw_result import ClaudeRawResult
from app.runtime.claude.runtime.adapter import ClaudeRuntimeAdapter
from app.runtime.claude.models.runtime_request import ClaudeRuntimeRequest
from app.runtime.claude.exceptions.runtime_error import ClaudeRuntimeError


def request(
    **overrides,
) -> ClaudeRuntimeRequest:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى request؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد ClaudeRuntimeRequest أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    values = {
        "job_id": "job-1",
        "job_type": "monitoring_cycle",
        "prompt": "Run the fixed workflow.",
        "timeout_seconds": 1.0,
    }
    values.update(overrides)
    return ClaudeRuntimeRequest(
        **values
    )


class Runner:
    """
    يمثل Runner جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(
        self,
        *,
        content=None,
        delay_seconds=0.0,
        error: Exception | None = None,
    ):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: content، delay_seconds، error.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.content = (
            content
            if content is not None
            else json.dumps(
                {
                    "status": "completed",
                    "summary": "Cycle complete.",
                    "data": {
                        "report_id": 123,
                    },
                    "metadata": {
                        "mode": "test",
                    },
                }
            )
        )
        self.delay_seconds = delay_seconds
        self.error = error
        self.cancelled_sessions = []

    async def run(
        self,
        runtime_request,
    ):
        """
        يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: runtime_request.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        if self.delay_seconds:
            await asyncio.sleep(
                self.delay_seconds
            )

        if self.error is not None:
            raise self.error

        return ClaudeRawResult(
            session_id="session-1",
            content=self.content,
            turn_count=2,
            tool_call_count=0,
            usage_metadata={
                "tokens": 42,
            },
        )

    async def cancel(
        self,
        session_id,
    ):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى cancel؛ المدخلات المهمة: session_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.cancelled_sessions.append(
            session_id
        )


def test_bounded_claude_invocation_succeeds():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_bounded_claude_invocation_succeeds؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner()
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.COMPLETED
    assert result.session_id == "session-1"
    assert result.error_code is None
    assert (
        result.structured_output.summary
        == "Cycle complete."
    )
    assert (
        result.structured_output.data["report_id"]
        == 123
    )
    assert result.turn_count == 2
    assert result.tool_call_count == 0
    assert result.usage_metadata["tokens"] == 42


def test_timeout_is_returned_as_controlled_result():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_timeout_is_returned_as_controlled_result؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner(
                delay_seconds=0.05,
            )
        ).execute(
            request(
                timeout_seconds=0.001,
            )
        )
    )

    assert result.status == ClaudeJobStatus.TIMED_OUT
    assert result.error_code == "timed_out"
    assert "exceeded" in result.error_message


def test_runtime_failure_is_returned_as_controlled_result():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_failure_is_returned_as_controlled_result؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner(
                error=ClaudeRuntimeError(
                    "Claude CLI failed."
                )
            )
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert result.error_code == "runtime_error"
    assert result.error_message == "Claude CLI failed."


def test_empty_runtime_exception_keeps_diagnostic_context():
    """
    يثبت أن الاستثناء الفارغ لا يتحول إلى سجل بلا رسالة تشخيصية.
    """
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner(
                error=ClaudeRuntimeError(),
            )
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert result.error_code == "runtime_error"
    assert result.error_message
    assert "ClaudeRuntimeError" in result.error_message


def test_empty_unexpected_exception_keeps_diagnostic_context():
    """
    يثبت أن الفشل غير المتوقع الفارغ يبقى قابلًا للتشخيص والتصفية.
    """
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner(
                error=ValueError(),
            )
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert result.error_code == "unexpected_error"
    assert result.error_message
    assert "ValueError" in result.error_message


def test_invalid_structured_output_is_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_invalid_structured_output_is_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner(
                content="not json"
            )
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert (
        result.error_code
        == "invalid_structured_output"
    )
    assert result.session_id == "session-1"


def test_operational_tool_access_is_disabled_in_c2():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_operational_tool_access_is_disabled_in_c2؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner()
        ).execute(
            request(
                allowed_tools=(
                    "run_monitoring",
                )
            )
        )
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert (
        result.error_code
        == "tool_access_disabled"
    )
    assert result.session_id is None


def test_claude_reported_failure_remains_failed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_claude_reported_failure_remains_failed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = asyncio.run(
        ClaudeRuntimeAdapter(
            runner=Runner(
                content=json.dumps(
                    {
                        "status": "failed",
                        "summary": "Could not complete.",
                    }
                )
            )
        ).execute(
            request()
        )
    )

    assert result.status == ClaudeJobStatus.FAILED
    assert (
        result.error_code
        == "claude_reported_failure"
    )
    assert result.error_message == "Could not complete."
