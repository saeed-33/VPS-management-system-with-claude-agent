"""Tests for test runtime composition.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_runtime_composition_is_outside_builder():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_composition_is_outside_builder؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")
    runtime = (
        ROOT / "app/composition/runtime.py"
    ).read_text(encoding="utf-8")

    assert "build_runtime_composition(" in builder

    for constructor in (
        "MonitoringService(",
        "ProjectMcpToolBoundary(",
        "OllamaClaudeCommandBuilder(",
        "SubprocessClaudeSessionRunner(",
        "ClaudeRuntimeAdapter(",
        "ClaudeNativeMonitoringRunner(",
        "ClaudeSupervisor(",
        "MonitoringScheduler(",
    ):
        assert constructor not in builder
        assert constructor in runtime


def test_runtime_composition_keeps_ollama_claude_contract():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_composition_keeps_ollama_claude_contract؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    runtime = (
        ROOT / "app/composition/runtime.py"
    ).read_text(encoding="utf-8")

    assert "claude_supervisor_runner = None" in runtime
    assert "base_url=settings.ollama_base_url" in runtime
    assert "settings.claude_runtime_executable" in runtime
    assert "settings.effective_claude_runtime_model" in runtime


def test_builder_is_composition_coordinator_after_a4_2d():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_builder_is_composition_coordinator_after_a4_2d؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")

    assert "build_repositories()" in builder
    assert "build_core_services(" in builder
    assert "build_retrieval_composition(" in builder
    assert "build_analysis_investigation_composition(" in builder
    assert "build_runtime_composition(" in builder
    assert "return ApplicationContainer(" in builder
