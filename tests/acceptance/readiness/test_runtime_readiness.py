"""Tests for test runtime readiness.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.interfaces.mcp.registry، app.interfaces.mcp.schemas، app.runtime.claude.result_parser، app.runtime.claude.exceptions.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from app.interfaces.mcp.registry import ProjectMcpToolBoundary
from app.interfaces.mcp.schemas.call import ProjectToolCall
from app.runtime.claude.result_parser import ClaudeStructuredResultParser
from app.runtime.claude.exceptions.structured_output_error import ClaudeStructuredOutputError
from tools.acceptance.evaluation.contracts import EvaluationMetric
from tools.acceptance.evaluation.safety_runtime import (
    evaluate_policy_cases,
    evaluate_provider_cases,
)


ROOT = Path(__file__).resolve().parents[1]


def _boundary() -> ProjectMcpToolBoundary:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى _boundary؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد ProjectMcpToolBoundary أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return ProjectMcpToolBoundary(
        server_service=None,
        monitoring_profile_service=None,
        monitoring_service=None,
        report_query_service=None,
    )


def test_c14_12_startup_recovers_interrupted_jobs():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_12_startup_recovers_interrupted_jobs؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    text = (ROOT / "app/main.py").read_text(encoding="utf-8")

    assert "recover_interrupted_jobs" in text
    assert "Recovered %s interrupted Claude agent job(s)." in text


def test_c14_12_mcp_surface_is_bounded_and_stable():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_12_mcp_surface_is_bounded_and_stable؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    boundary = _boundary()
    definitions = boundary.list_tools()

    assert len(definitions) == 25
    expected_bounded_write_ids = {
        "apply_approved_remediation",
        "create_remediation_plan",
        "request_user_approval",
        "run_specialist",
        "start_investigation",
            "test_remediation_in_sandbox",
            "attempt_autonomous_remediation",
        }
    assert {
        item.tool_id
        for item in definitions
        if not item.read_only
    } == expected_bounded_write_ids

    forbidden = (
        "raw_ssh",
        "raw_sql",
        "execute_command",
        "database_query",
        "psql",
        "shell",
        "arbitrary filesystem",
        "unbounded subprocess",
    )
    serialized = json.dumps(
        [
            {
                "tool_id": item.tool_id,
                "description": item.description,
                "input_schema": item.input_schema,
            }
            for item in definitions
        ],
        sort_keys=True,
    ).lower()

    assert all(term not in serialized for term in forbidden)


def test_c14_12_unknown_and_unregistered_tools_fail_closed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_12_unknown_and_unregistered_tools_fail_closed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    async def run() -> None:
        """
        يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        for tool_id in (
            "raw_ssh",
            "raw_sql",
            "execute_command",
            "database_query",
        ):
            result = await _boundary().execute(
                ProjectToolCall(tool_id=tool_id, arguments={})
            )
            assert result.success is False
            assert result.error_code == "unknown_tool"

    asyncio.run(run())


def test_c14_12_claude_malformed_output_fails_closed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_12_claude_malformed_output_fails_closed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    parser = ClaudeStructuredResultParser()

    try:
        parser.parse("not-json")
    except ClaudeStructuredOutputError:
        pass
    else:
        raise AssertionError("Malformed Claude output was accepted.")


def test_c14_12_controlled_policy_and_provider_failures_are_measured():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_12_controlled_policy_and_provider_failures_are_measured؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    policy = evaluate_policy_cases()
    provider = asyncio.run(evaluate_provider_cases())

    assert len(policy) == 10
    assert len(provider) == 10
    assert all(item.passed for item in policy)
    assert all(item.passed for item in provider)
    assert {item.metric for item in policy} == {
        EvaluationMetric.POLICY_SAFETY
    }
    assert {item.metric for item in provider} == {
        EvaluationMetric.PROVIDER_RESILIENCE
    }
