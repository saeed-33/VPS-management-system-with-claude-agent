from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_hybrid_does_not_use_rrf_as_vector_similarity():
    source = (
        ROOT
        / "app/agent/analysis/retrieval/hybrid_retriever.py"
    ).read_text(encoding="utf-8")

    assert "vector_score=candidate.vector_score" in source
    assert "score=candidate.rrf_score" in source


def test_orchestrator_persists_vector_similarity_not_rrf():
    source = (
        ROOT
        / "app/agent/analysis/analysis_orchestrator.py"
    ).read_text(encoding="utf-8")

    assert "retrieved_contexts[0].vector_score" in source
    assert '"similarity_score": item.vector_score' in source


def test_vector_repository_filters_before_limit():
    source = (
        ROOT
        / "app/shared/database/repositories/retrieval_repository.py"
    ).read_text(encoding="utf-8")

    distance_filter = "distance <= maximum_distance"
    limit_call = ".limit(limit)"

    assert distance_filter in source
    assert source.index(distance_filter) < source.index(
        limit_call,
        source.index("def find_similar("),
    )
