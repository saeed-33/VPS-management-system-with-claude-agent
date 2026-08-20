"""Tests for test ollama runtime contract.
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


def test_c14_11a3_removes_legacy_runtime_surfaces():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_11a3_removes_legacy_runtime_surfaces؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert not (ROOT / "app/domain").exists()
    assert not (ROOT / "app/admin").exists()
    assert not (ROOT / "app/mcp").exists()
    assert not (ROOT / "app/interfaces/mcp/project_boundary_parts").exists()
    assert not (
        ROOT / "app/.python-version"
    ).exists()


def test_c14_11a3_runtime_dependencies_are_ollama_only():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_11a3_runtime_dependencies_are_ollama_only؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    pyproject = (
        ROOT / "pyproject.toml"
    ).read_text(encoding="utf-8").lower()

    assert '"openai' not in pyproject
    assert '"langgraph' not in pyproject

    config = (
        ROOT / "app/core/config.py"
    ).read_text(encoding="utf-8")

    assert 'Literal["ollama"]' in config
    assert "openai_api_key" not in config
    assert "openai_model" not in config


def test_c14_11a3_no_openai_implementation_surfaces_remain():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_11a3_no_openai_implementation_surfaces_remain؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    paths = (
        ROOT / "app/composition/analysis/client_factory.py",
        ROOT / "app/composition/investigation/final_diagnosis_narrative_client_factory.py",
        ROOT / "app/composition/investigation/specialist_reasoning_client_factory.py",
    )

    joined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in paths
    )

    assert "OpenAIAnalysisClient" not in joined
    assert "OpenAIFinalDiagnosisNarrativeClient" not in joined
    assert "OpenAISpecialistReasoningClient" not in joined
    assert 'llm_provider == "openai"' not in joined
    assert "from openai import" not in joined


def test_c14_11a3_ollama_implementations_remain():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_11a3_ollama_implementations_remain؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    final_diag = (
        ROOT / "app/composition/investigation/final_diagnosis_narrative_client_factory.py"
    ).read_text(encoding="utf-8")
    specialist = (
        ROOT / "app/composition/investigation/specialist_reasoning_client_factory.py"
    ).read_text(encoding="utf-8")

    assert "OllamaFinalDiagnosisNarrativeClient" in final_diag
    assert "OllamaSpecialistReasoningClient" in specialist
