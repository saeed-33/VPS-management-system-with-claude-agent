"""Tests for test ollama boundary.
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


def test_ollama_provider_implementations_live_in_infrastructure():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_ollama_provider_implementations_live_in_infrastructure؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    analysis = (
        ROOT / "app/infrastructure/llm/ollama/analysis_client.py"
    ).read_text(encoding="utf-8")
    embedding = (
        ROOT / "app/infrastructure/llm/ollama/embedding_client.py"
    ).read_text(encoding="utf-8")

    assert "class OllamaAnalysisClient" in analysis
    assert "class OllamaEmbeddingClient" in embedding
    assert "import httpx" in analysis
    assert "import httpx" in embedding


def test_analysis_capability_factories_use_infrastructure_implementations():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_analysis_capability_factories_use_infrastructure_implementations؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    analysis_factory = (
        ROOT / "app/capabilities/analysis/client_factory.py"
    ).read_text(encoding="utf-8")
    embedding_factory = (
        ROOT / "app/capabilities/analysis/retrieval/embedding_factory.py"
    ).read_text(encoding="utf-8")

    assert "app.infrastructure.llm.ollama.analysis_client" in analysis_factory
    assert "app.infrastructure.llm.ollama.embedding_client" in embedding_factory
    assert "app.capabilities.analysis.ollama_client" not in analysis_factory
    assert (
        "app.capabilities.analysis.retrieval.ollama_embedding_client"
        not in embedding_factory
    )


def test_legacy_ollama_modules_are_removed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_legacy_ollama_modules_are_removed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert not (ROOT / "app/domain").exists()
