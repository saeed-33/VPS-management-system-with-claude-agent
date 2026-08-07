import asyncio
import json
from dataclasses import dataclass

import pytest

from app.agent.analysis.retrieval.full_text_retriever import (
    FullTextCandidate,
)
from app.agent.analysis.retrieval.hybrid_retriever import (
    HybridRetriever,
)
from app.agent.analysis.retrieval.rag_context import (
    RetrievedAnalysisContext,
)
from app.agent.analysis.retrieval.structured_compatibility import (
    StructuredCompatibilityChecker,
)


@dataclass
class FakeAnalysis:
    status: str = "completed"
    health_status: str = "healthy"
    summary: str = "summary"
    issues: list | None = None
    positive_findings: list | None = None
    recommended_actions: list | None = None

    def __post_init__(self):
        self.issues = self.issues or []
        self.positive_findings = (
            self.positive_findings or []
        )
        self.recommended_actions = (
            self.recommended_actions or []
        )


@dataclass
class FakeDocument:
    normalized_text: str


class FakeAnalysisRepository:
    def __init__(self, analyses):
        self.analyses = analyses

    def get_by_id(self, analysis_id):
        return self.analyses.get(analysis_id)


class FakeRetrievalRepository:
    def __init__(self, documents=None):
        self.documents = documents or {}

    def get_by_analysis_id(self, analysis_id):
        return self.documents.get(analysis_id)


class FakeVectorRetriever:
    def __init__(self, contexts):
        self.contexts = contexts

    async def retrieve(self, **kwargs):
        return list(self.contexts)


class FakeFullTextRetriever:
    def __init__(self, candidates):
        self.candidates = candidates

    def retrieve(self, **kwargs):
        return list(self.candidates)


def normalized_report(
    *,
    connection_successful=True,
    success=True,
    exit_status=0,
):
    return json.dumps(
        {
            "connection_successful": connection_successful,
            "error_message": "",
            "executions": [
                {
                    "command_id": 10,
                    "success": success,
                    "exit_status": exit_status,
                    "error_message": "",
                    "stderr": "",
                }
            ],
        },
        sort_keys=True,
    )


def vector_context(
    *,
    analysis_id,
    report_id,
    score,
):
    return RetrievedAnalysisContext(
        source_report_id=report_id,
        source_analysis_id=analysis_id,
        score=score,
        rank=1,
        health_status="healthy",
        summary="historical",
        issues=[],
        positive_findings=[],
        recommended_actions=[],
    )


def run_retrieve(retriever, current):
    return asyncio.run(
        retriever.retrieve(
            normalized_report=current,
            server_id=1,
            monitoring_profile_id=2,
            command_set_hash="abc",
            exclude_report_id=999,
        )
    )


def test_weak_vector_candidate_is_rejected_even_with_full_text():
    vector = FakeVectorRetriever(
        [
            vector_context(
                analysis_id=1,
                report_id=101,
                score=0.40,
            )
        ]
    )
    text = FakeFullTextRetriever(
        [
            FullTextCandidate(
                report_id=101,
                analysis_id=1,
                rank=99.0,
                health_status="healthy",
            )
        ]
    )

    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(),
        compatibility_checker=None,
        vector_retriever=vector,
        full_text_retriever=text,
        top_k=3,
        minimum_vector_score=0.72,
    )

    assert run_retrieve(
        retriever,
        normalized_report(),
    ) == []


def test_full_text_only_candidate_never_bypasses_vector_threshold():
    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(),
        compatibility_checker=None,
        vector_retriever=FakeVectorRetriever([]),
        full_text_retriever=FakeFullTextRetriever(
            [
                FullTextCandidate(
                    report_id=101,
                    analysis_id=1,
                    rank=500.0,
                    health_status="healthy",
                )
            ]
        ),
        minimum_vector_score=0.72,
    )

    assert run_retrieve(
        retriever,
        normalized_report(),
    ) == []


def test_hybrid_candidate_preserves_real_vector_similarity():
    vector = FakeVectorRetriever(
        [
            vector_context(
                analysis_id=1,
                report_id=101,
                score=0.96,
            )
        ]
    )
    text = FakeFullTextRetriever(
        [
            FullTextCandidate(
                report_id=101,
                analysis_id=1,
                rank=0.15,
                health_status="healthy",
            )
        ]
    )

    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(),
        compatibility_checker=None,
        vector_retriever=vector,
        full_text_retriever=text,
        top_k=1,
        rrf_k=60,
        minimum_vector_score=0.72,
    )

    contexts = run_retrieve(
        retriever,
        normalized_report(),
    )

    assert len(contexts) == 1
    context = contexts[0]
    assert context.retrieval_strategy == "hybrid"
    assert context.vector_score == pytest.approx(0.96)
    assert context.text_score == pytest.approx(0.15)
    assert context.score == pytest.approx(2 / 61)
    assert context.score != context.vector_score


def test_structural_conflict_rejects_high_similarity_candidate():
    current = normalized_report(
        connection_successful=True,
    )
    historical = normalized_report(
        connection_successful=False,
    )

    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(
            {
                1: FakeDocument(
                    normalized_text=historical
                )
            }
        ),
        compatibility_checker=(
            StructuredCompatibilityChecker()
        ),
        vector_retriever=FakeVectorRetriever(
            [
                vector_context(
                    analysis_id=1,
                    report_id=101,
                    score=0.99,
                )
            ]
        ),
        full_text_retriever=None,
        minimum_vector_score=0.72,
    )

    assert run_retrieve(retriever, current) == []


def test_compatible_candidate_is_accepted():
    current = normalized_report()

    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(
            {
                1: FakeDocument(
                    normalized_text=current
                )
            }
        ),
        compatibility_checker=(
            StructuredCompatibilityChecker()
        ),
        vector_retriever=FakeVectorRetriever(
            [
                vector_context(
                    analysis_id=1,
                    report_id=101,
                    score=0.95,
                )
            ]
        ),
        full_text_retriever=None,
        minimum_vector_score=0.72,
    )

    contexts = run_retrieve(retriever, current)

    assert len(contexts) == 1
    assert contexts[0].vector_score == pytest.approx(0.95)


def test_duplicate_vector_and_text_candidate_becomes_one_context():
    vector = FakeVectorRetriever(
        [
            vector_context(
                analysis_id=1,
                report_id=101,
                score=0.93,
            )
        ]
    )
    text = FakeFullTextRetriever(
        [
            FullTextCandidate(
                report_id=101,
                analysis_id=1,
                rank=0.2,
                health_status="healthy",
            )
        ]
    )

    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(),
        compatibility_checker=None,
        vector_retriever=vector,
        full_text_retriever=text,
        top_k=3,
        minimum_vector_score=0.72,
    )

    contexts = run_retrieve(
        retriever,
        normalized_report(),
    )

    assert len(contexts) == 1
    assert contexts[0].source_analysis_id == 1
