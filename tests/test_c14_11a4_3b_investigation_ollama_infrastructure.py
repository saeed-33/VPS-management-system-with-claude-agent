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
import ast


ROOT = Path(__file__).resolve().parents[1]


def test_investigation_ollama_adapters_live_in_infrastructure():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_investigation_ollama_adapters_live_in_infrastructure؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    specialist = (
        ROOT
        / "app/infrastructure/llm/ollama/specialist_reasoning_client.py"
    ).read_text(encoding="utf-8")
    final = (
        ROOT
        / "app/infrastructure/llm/ollama/final_diagnosis_client.py"
    ).read_text(encoding="utf-8")

    assert "class OllamaSpecialistReasoningClient" in specialist
    assert "class OllamaFinalDiagnosisNarrativeClient" in final
    assert "import httpx" in specialist
    assert "import httpx" in final


def test_investigation_capability_keeps_contracts_not_ollama_implementations():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_investigation_capability_keeps_contracts_not_ollama_implementations؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    specialist = (
        ROOT
        / "app/capabilities/investigation/specialist_reasoning_client.py"
    ).read_text(encoding="utf-8")
    final = (
        ROOT
        / "app/capabilities/investigation/final_diagnosis_synthesizer.py"
    ).read_text(encoding="utf-8")

    specialist_contract = (
        ROOT / "app/core/contracts/specialist_reasoning.py"
    ).read_text(encoding="utf-8")
    final_contract = (
        ROOT / "app/core/contracts/final_diagnosis.py"
    ).read_text(encoding="utf-8")

    assert "class SpecialistReasoningClient" in specialist_contract
    assert "class FinalDiagnosisNarrativeClient" in final_contract
    assert "app.core.contracts.specialist_reasoning" in specialist
    assert "app.core.contracts.final_diagnosis" in final

    assert "class OllamaSpecialistReasoningClient" not in specialist
    assert "class OllamaFinalDiagnosisNarrativeClient" not in final

    assert (
        "app.infrastructure.llm.ollama.specialist_reasoning_client"
        in specialist
    )
    assert (
        "app.infrastructure.llm.ollama.final_diagnosis_client"
        in final
    )


def test_capability_contracts_resolve_provider_adapters_lazily():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_capability_contracts_resolve_provider_adapters_lazily؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    specialist = (
        ROOT
        / "app/capabilities/investigation/specialist_reasoning_client.py"
    ).read_text(encoding="utf-8")
    final = (
        ROOT
        / "app/capabilities/investigation/final_diagnosis_synthesizer.py"
    ).read_text(encoding="utf-8")

    assert any(
        isinstance(node, ast.FunctionDef)
        and node.name == "__getattr__"
        for node in ast.parse(specialist).body
    )
    assert any(
        isinstance(node, ast.FunctionDef)
        and node.name == "__getattr__"
        for node in ast.parse(final).body
    )
