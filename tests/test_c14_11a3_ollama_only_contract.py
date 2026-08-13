from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_c14_11a3_removes_legacy_runtime_surfaces():
    assert not (ROOT / "app/domain").exists()
    assert not (ROOT / "app/admin").exists()
    assert not (ROOT / "app/mcp").exists()
    assert not (ROOT / "app/interfaces/mcp/project_boundary_parts").exists()
    assert not (
        ROOT / "app/.python-version"
    ).exists()


def test_c14_11a3_runtime_dependencies_are_ollama_only():
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
    paths = (
        ROOT / "app/capabilities/analysis/client_factory.py",
        ROOT / "app/capabilities/investigation/final_diagnosis_synthesizer.py",
        ROOT / "app/capabilities/investigation/specialist_reasoning_client.py",
        ROOT / "app/capabilities/investigation/__init__.py",
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
    final_diag = (
        ROOT / "app/capabilities/investigation/final_diagnosis_synthesizer.py"
    ).read_text(encoding="utf-8")
    specialist = (
        ROOT / "app/capabilities/investigation/specialist_reasoning_client.py"
    ).read_text(encoding="utf-8")

    assert "OllamaFinalDiagnosisNarrativeClient" in final_diag
    assert "OllamaSpecialistReasoningClient" in specialist
