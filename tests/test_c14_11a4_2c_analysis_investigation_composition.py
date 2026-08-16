"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_analysis_and_investigation_composition_is_outside_builder():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_analysis_and_investigation_composition_is_outside_builder؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")
    analysis = (
        ROOT / "app/composition/analysis.py"
    ).read_text(encoding="utf-8")

    assert "build_retrieval_composition(" in builder
    assert "build_analysis_investigation_composition(" in builder

    assert "AnalysisOrchestrator(" not in builder
    assert "SpecialistInvestigationLoop(" not in builder
    assert "KnowledgeHybridRetriever(" not in builder
    assert "HybridRetriever(" not in builder

    assert "AnalysisOrchestrator(" in analysis
    assert "SpecialistInvestigationLoop(" in analysis
    assert "KnowledgeHybridRetriever(" in analysis
    assert "HybridRetriever(" in analysis


def test_claude_mcp_and_scheduler_wiring_moves_to_runtime_composition():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_claude_mcp_and_scheduler_wiring_moves_to_runtime_composition؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")
    runtime = (
        ROOT / "app/composition/runtime.py"
    ).read_text(encoding="utf-8")

    for constructor in (
        "ProjectMcpToolBoundary(",
        "ClaudeNativeMonitoringRunner(",
        "MonitoringScheduler(",
    ):
        assert constructor not in builder
        assert constructor in runtime

