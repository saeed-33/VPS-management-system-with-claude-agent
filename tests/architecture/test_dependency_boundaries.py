"""Tests for test dependency boundaries.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app"


def _module_name(path: Path) -> str:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى _module_name؛ المدخلات المهمة: path.
    تعيد str أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    relative = path.relative_to(ROOT).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _imports(path: Path) -> set[str]:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى _imports؛ المدخلات المهمة: path.
    تعيد set[str] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)

    return {name for name in result if name == "app" or name.startswith("app.")}


def _violations(
    package: str,
    forbidden_prefixes: tuple[str, ...],
) -> list[str]:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى _violations؛ المدخلات المهمة: package، forbidden_prefixes.
    تعيد list[str] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    violations: list[str] = []
    root = ROOT / package.replace(".", "/")

    for path in root.rglob("*.py"):
        for imported in _imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(
                    f"{path.relative_to(ROOT)} -> {imported}"
                )

    return violations


def test_core_has_no_outer_layer_dependencies():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_core_has_no_outer_layer_dependencies؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert _violations(
        "app/core",
        (
            "app.infrastructure",
            "app.interfaces",
            "app.composition",
            "app.capabilities",
            "app.runtime",
        ),
    ) == []


def test_capabilities_do_not_depend_on_interfaces_composition_or_runtime():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_capabilities_do_not_depend_on_interfaces_composition_or_runtime؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert _violations(
        "app/capabilities",
        (
            "app.interfaces",
            "app.composition",
            "app.runtime",
        ),
    ) == []


def test_investigation_does_not_depend_on_analysis_or_knowledge_implementations():
    """تمنع اعتماد التحقيق المباشر على قدرات التحليل والمعرفة."""
    assert _violations(
        "app/capabilities/investigation",
        (
            "app.capabilities.analysis",
            "app.capabilities.knowledge",
        ),
    ) == []


def test_monitoring_and_remediation_do_not_depend_on_each_other():
    """تثبت استقلال قدرات المراقبة والمعالجة عن بعضها."""
    assert _violations(
        "app/capabilities/monitoring",
        ("app.capabilities.remediation",),
    ) == []
    assert _violations(
        "app/capabilities/remediation",
        ("app.capabilities.monitoring",),
    ) == []


def test_infrastructure_does_not_depend_on_interface_or_runtime_layers():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_infrastructure_does_not_depend_on_interface_or_runtime_layers؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert _violations(
        "app/infrastructure",
        (
            "app.interfaces",
            "app.composition",
            "app.runtime",
        ),
    ) == []


def test_legacy_application_packages_are_absent():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_legacy_application_packages_are_absent؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert not (APP / "shared").exists()
    assert not (APP / "tools").exists()
    assert not (APP / "domain").exists()
    assert not (APP / "admin").exists()
    assert not (APP / "mcp").exists()
    assert not (APP / "interfaces" / "mcp" / "project_boundary_parts").exists()


def test_application_sources_do_not_import_deleted_namespaces():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_application_sources_do_not_import_deleted_namespaces؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    forbidden = (
        "app.domain",
        "app.admin",
        "app.mcp",
        "app.shared",
        "app.tools",
    )
    offenders: list[str] = []
    for path in (ROOT / "app").rglob("*.py"):
        for imported in _imports(path):
            if imported.startswith(forbidden):
                offenders.append(f"{path.relative_to(ROOT)} -> {imported}")
    assert offenders == []


def test_application_import_graph_is_acyclic():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_application_import_graph_is_acyclic؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    module_paths = {
        _module_name(path): path
        for path in APP.rglob("*.py")
    }
    graph = {
        module: {
            imported
            for imported in _imports(path)
            if imported in module_paths
        }
        for module, path in module_paths.items()
    }

    visiting: list[str] = []
    visited: set[str] = set()
    cycles: list[str] = []

    def visit(module: str) -> None:
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى visit؛ المدخلات المهمة: module.
        تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        if module in visiting:
            start = visiting.index(module)
            cycles.append(" -> ".join(visiting[start:] + [module]))
            return
        if module in visited:
            return

        visiting.append(module)
        for dependency in sorted(graph[module]):
            visit(dependency)
        visiting.pop()
        visited.add(module)

    for module in sorted(graph):
        visit(module)

    assert cycles == []
