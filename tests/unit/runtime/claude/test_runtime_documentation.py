"""Tests for test runtime documentation.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def read_doc(
    relative_path: str,
) -> str:
    """
    يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى read_doc؛ المدخلات المهمة: relative_path.
    تعيد str أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return (
        ROOT
        / relative_path
    ).read_text(
        encoding="utf-8",
    )


def test_project_structure_documents_runtime_files():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_project_structure_documents_runtime_files؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    project_structure = read_doc(
        "docs/PROJECT_STRUCTURE.md"
    )

    required_entries = [
        "CLAUDE.md",
        ".mcp.json",
        ".claude/settings.json",
        "app/runtime/claude/supervisor/supervisor.py",
            "app/interfaces/mcp/registry.py",
        "app/interfaces/mcp/catalog.py",
            "app/interfaces/admin/api/system.py",
            "app/interfaces/admin/web/templates/system.html",
        "docs/operations/claude-runtime.md",
    ]

    for entry in required_entries:
        assert entry in project_structure


def test_runtime_operations_doc_matches_configured_ollama_defaults():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_operations_doc_matches_configured_ollama_defaults؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    runtime_doc = read_doc(
        "docs/operations/claude-runtime.md"
    )
    config_doc = read_doc(
        "docs/operations/configuration.md"
    )
    env_example = read_doc(
        ".env.example"
    )

    assert "OLLAMA_MODEL=qwen3:8b" in runtime_doc
    assert "ollama pull qwen3:8b" in runtime_doc
    assert "OLLAMA_MODEL=qwen3:8b" in config_doc
    assert "OLLAMA_MODEL=qwen3:8b" in env_example


def test_runtime_documentation_has_current_verification_commands():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_documentation_has_current_verification_commands؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    runtime_doc = read_doc(
        "docs/operations/claude-runtime.md"
    )

    assert "app\\runtime" in runtime_doc
    assert "app\\interfaces" in runtime_doc
    assert "app\\integrations" not in runtime_doc


def test_r5_status_and_test_catalog_are_documented():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_r5_status_and_test_catalog_are_documented؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    roadmap = read_doc(
        "docs/roadmap/claude-runtime-implementation-plan.md"
    )
    status = read_doc(
        "docs/PROJECT_STATUS.md"
    )
    test_catalog = read_doc(
        "docs/testing/TEST_CATALOG.md"
    )

    assert "R.5 - Documentation and Tests" in roadmap
    assert "R.5 Documentation and Tests: complete" in status
    assert (
        "tests/unit/runtime/claude/test_runtime_documentation.py"
        in test_catalog
    )
