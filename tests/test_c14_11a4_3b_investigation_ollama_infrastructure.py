from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]


def test_investigation_ollama_adapters_live_in_infrastructure():
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


def test_domain_keeps_contracts_not_ollama_implementations():
    specialist = (
        ROOT
        / "app/domain/investigation/specialist_reasoning_client.py"
    ).read_text(encoding="utf-8")
    final = (
        ROOT
        / "app/domain/investigation/final_diagnosis_synthesizer.py"
    ).read_text(encoding="utf-8")

    assert "class SpecialistReasoningClient" in specialist
    assert "class FinalDiagnosisNarrativeClient" in final

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


def test_legacy_class_names_have_compatibility_getattr():
    specialist = (
        ROOT
        / "app/domain/investigation/specialist_reasoning_client.py"
    ).read_text(encoding="utf-8")
    final = (
        ROOT
        / "app/domain/investigation/final_diagnosis_synthesizer.py"
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
