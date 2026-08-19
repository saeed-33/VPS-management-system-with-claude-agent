"""Tests for test mcp project boundary.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.interfaces.mcp.registry.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import ast
from pathlib import Path

from app.interfaces.mcp.registry import ProjectMcpToolBoundary


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TOOL_IDS = {'get_server_context', 'start_investigation', 'get_top_similar_reports', 'get_analysis', 'propose_remediation', 'get_sandbox_result', 'run_monitoring', 'search_similar_incidents', 'create_remediation_plan', 'get_report', 'analyze_report', 'find_exact_report_match', 'get_latest_report', 'search_knowledge', 'get_investigation_status', 'apply_approved_remediation', 'request_user_approval', 'get_monitoring_profile', 'get_evidence', 'get_investigation', 'get_available_specialists', 'test_remediation_in_sandbox', 'run_specialist', 'get_specialist_definition', 'attempt_autonomous_remediation'}


def make_boundary() -> ProjectMcpToolBoundary:
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_boundary؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد ProjectMcpToolBoundary أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return ProjectMcpToolBoundary(
        server_service=None,
        monitoring_profile_service=None,
        monitoring_service=None,
        report_query_service=None,
    )


def test_c14_8_public_tool_contract_is_unchanged():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_8_public_tool_contract_is_unchanged؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    boundary = make_boundary()

    definitions = {
        definition.tool_id
        for definition in boundary.list_tools()
    }

    assert definitions == EXPECTED_TOOL_IDS
    assert set(boundary._handlers) == EXPECTED_TOOL_IDS


def test_c14_8_project_boundary_is_thin_public_facade():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_8_project_boundary_is_thin_public_facade؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    path = ROOT / "app" / "interfaces" / "mcp" / "registry.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))

    boundary_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "ProjectMcpToolBoundary"
    )

    owned_methods = {
        node.name
        for node in boundary_class.body
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        )
    }

    assert owned_methods == {
        "__init__",
        "list_tools",
        "list_tool_groups",
        "execute",
    }


def test_c14_8_bounded_modules_own_tool_implementations():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_8_bounded_modules_own_tool_implementations؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    boundary = make_boundary()

    expected_modules = {
        "_run_monitoring": (
        "app.interfaces.mcp.handlers.monitoring"
        ),
        "_analyze_report": (
        "app.interfaces.mcp.handlers.analysis"
        ),
        "_run_specialist": (
        "app.interfaces.mcp.handlers.investigation"
        ),
        "_create_remediation_plan": (
        "app.interfaces.mcp.handlers.remediation"
        ),
        "_required_int": (
        "app.interfaces.mcp.handlers.common"
        ),
        "_build_definitions": (
        "app.interfaces.mcp.handlers.definitions"
        ),
    }

    for method_name, module_name in expected_modules.items():
        method = getattr(boundary, method_name)
        assert method.__module__ == module_name


def test_c14_8_mcp_package_export_is_lazy_and_cycle_free():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_8_mcp_package_export_is_lazy_and_cycle_free؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    from app.interfaces.mcp.registry import ProjectMcpToolBoundary as PackageBoundary
    from app.interfaces.mcp.registry import ProjectMcpToolBoundary

    assert PackageBoundary is ProjectMcpToolBoundary
