"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.runtime.claude.observability.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from app.runtime.claude.observability import (
    ClaudeAgentObservabilityService,
)


class FakeRepository:
    """
    يمثل FakeRepository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, items) -> None:
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: items.
        تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.items = list(items)

    def get_by_job_id(self, job_id: str):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_by_job_id؛ المدخلات المهمة: job_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return next(
            (
                item
                for item in self.items
                if item.job_id == job_id
            ),
            None,
        )

    def list_recent(
        self,
        *,
        limit=100,
        server_id=None,
        status=None,
    ):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_recent؛ المدخلات المهمة: limit، server_id، status.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        items = self.items

        if server_id is not None:
            items = [
                item
                for item in items
                if item.server_id == server_id
            ]

        if status is not None:
            items = [
                item
                for item in items
                if item.status == status
            ]

        return items[:limit]


def make_job(
    *,
    job_id="job-1",
    status="completed",
    tools=None,
    mcp_status="connected",
    duration_ms=1200,
    error_code=None,
    error_message=None,
):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_job؛ المدخلات المهمة: job_id، status، tools، mcp_status، duration_ms.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    started_at = datetime(
        2026,
        8,
        13,
        tzinfo=UTC,
    )

    tools = list(tools or ())

    return SimpleNamespace(
        job_id=job_id,
        job_type="monitoring_cycle",
        server_id=2,
        status=status,
        claude_session_id="session-1",
        created_at=started_at,
        started_at=started_at,
        completed_at=(
            started_at
            + timedelta(milliseconds=duration_ms)
        ),
        turn_count=8,
        tool_call_count=len(tools),
        usage_metadata={
            "duration_ms": duration_ms,
            "duration_api_ms": duration_ms - 100,
            "input_tokens": 1000,
            "output_tokens": 200,
            "total_cost_usd": 0.01,
            "subtype": "success",
            "stop_reason": "end_turn",
            "is_error": False,
            "event_tool_names": tools,
            "event_mcp_servers": [
                {
                    "name": "vps",
                    "status": mcp_status,
                }
            ],
            "modelUsage": {
                "gemma-test": {
                    "inputTokens": 1000,
                    "outputTokens": 200,
                }
            },
        },
        job_metadata={
            "runtime": "claude_code",
            "provider": "ollama",
            "agent": "server-supervisor",
            "max_turns": 20,
            "allowed_tools": [
                "mcp__vps__run_monitoring",
            ],
        },
        error_code=error_code,
        error_message=error_message,
    )


def test_trace_normalizes_runtime_evidence():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_trace_normalizes_runtime_evidence؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    job = make_job(
        tools=[
            "mcp__vps__get_server_context",
            "mcp__vps__run_monitoring",
            "mcp__vps__analyze_report",
            "mcp__vps__start_investigation",
            "mcp__vps__run_specialist",
        ]
    )

    service = ClaudeAgentObservabilityService(
        FakeRepository([job])
    )

    trace = service.get_trace("job-1")

    assert trace is not None
    assert trace["required_tools_verified"] is True
    assert trace["mcp_connected"] is True
    assert trace["investigation_started"] is True
    assert trace["specialist_delegation_count"] == 1
    assert trace["duration_ms"] == 1200
    assert trace["input_tokens"] == 1000


def test_summary_exposes_failures_tools_and_mcp_health():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_summary_exposes_failures_tools_and_mcp_health؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    completed = make_job(
        job_id="job-ok",
        tools=[
            "mcp__vps__run_monitoring",
            "mcp__vps__analyze_report",
            "mcp__vps__run_specialist",
        ],
    )
    failed = make_job(
        job_id="job-failed",
        status="failed",
        tools=[
            "mcp__vps__run_monitoring",
        ],
        mcp_status="failed",
        duration_ms=800,
        error_code="runtime_error",
        error_message="Claude process failed.",
    )

    service = ClaudeAgentObservabilityService(
        FakeRepository(
            [completed, failed]
        )
    )

    summary = service.summarize_recent()

    assert summary["sample_size"] == 2
    assert summary["completed_count"] == 1
    assert summary["failed_count"] == 1
    assert summary["success_rate"] == 0.5
    assert summary["terminal_success_rate"] == 0.5
    assert summary["active_count"] == 0
    assert summary["terminal_count"] == 2
    assert summary["error_code_counts"] == {
        "runtime_error": 1,
    }
    assert summary["diagnostic_gap_count"] == 0
    assert summary["mcp_disconnected_job_count"] == 1
    assert summary["specialist_delegation_count"] == 1


def test_summary_separates_active_jobs_and_missing_diagnostics():
    """
    يثبت أن الملخص يميز المهام النشطة عن الفشل النهائي ويكشف فجوات التشخيص.
    """
    running = make_job(
        job_id="job-running",
        status="running",
    )
    failed_without_message = make_job(
        job_id="job-empty-error",
        status="failed",
    )

    summary = ClaudeAgentObservabilityService(
        FakeRepository(
            [running, failed_without_message]
        )
    ).summarize_recent()

    assert summary["active_count"] == 1
    assert summary["terminal_count"] == 1
    assert summary["diagnostic_gap_count"] == 1
    assert summary["terminal_success_rate"] == 0.0


def test_completed_job_missing_required_tools_is_visible():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_completed_job_missing_required_tools_is_visible؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    job = make_job(
        tools=[
            "mcp__vps__run_monitoring",
        ]
    )

    service = ClaudeAgentObservabilityService(
        FakeRepository([job])
    )

    summary = service.summarize_recent()

    assert (
        summary[
            "required_tool_verification_failure_count"
        ]
        == 1
    )


def test_missing_job_returns_none():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_missing_job_returns_none؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = ClaudeAgentObservabilityService(
        FakeRepository([])
    )

    assert service.get_trace("missing") is None
