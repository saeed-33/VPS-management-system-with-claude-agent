from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]


def test_ollama_provider_implementations_live_in_infrastructure():
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


def test_domain_factories_use_infrastructure_implementations():
    analysis_factory = (
        ROOT / "app/domain/analysis/client_factory.py"
    ).read_text(encoding="utf-8")
    embedding_factory = (
        ROOT / "app/domain/analysis/retrieval/embedding_factory.py"
    ).read_text(encoding="utf-8")

    assert "app.infrastructure.llm.ollama.analysis_client" in analysis_factory
    assert "app.infrastructure.llm.ollama.embedding_client" in embedding_factory
    assert "app.domain.analysis.ollama_client" not in analysis_factory
    assert (
        "app.domain.analysis.retrieval.ollama_embedding_client"
        not in embedding_factory
    )


def test_legacy_ollama_modules_are_thin_facades():
    analysis = (
        ROOT / "app/domain/analysis/ollama_client.py"
    ).read_text(encoding="utf-8")
    embedding = (
        ROOT / "app/domain/analysis/retrieval/ollama_embedding_client.py"
    ).read_text(encoding="utf-8")

    assert not any(
        isinstance(node, ast.ClassDef)
        for node in ast.parse(analysis).body
    )
    assert not any(
        isinstance(node, ast.ClassDef)
        for node in ast.parse(embedding).body
    )
