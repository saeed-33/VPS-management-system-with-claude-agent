"""Tests for batched historical analysis hydration."""
import asyncio
from types import SimpleNamespace

from app.capabilities.analysis.retrieval.rag_retriever import RagRetriever


def test_rag_retriever_hydrates_candidates_with_one_bulk_query():
    retrieval_calls = []
    hydration_calls = []

    async def embed(_text):
        return [0.1, 0.2, 0.3]

    def find_similar(**kwargs):
        retrieval_calls.append(kwargs)
        return [
            (SimpleNamespace(analysis_id=11, report_id=101), 0.91),
            (SimpleNamespace(analysis_id=12, report_id=102), 0.84),
        ]

    def get_by_ids(analysis_ids):
        hydration_calls.append(analysis_ids)
        return {
            11: SimpleNamespace(
                status="completed",
                health_status="healthy",
                summary="first",
                issues=[],
                positive_findings=[],
                recommended_actions=[],
            ),
            12: SimpleNamespace(
                status="completed",
                health_status="degraded",
                summary="second",
                issues=[],
                positive_findings=[],
                recommended_actions=[],
            ),
        }

    retriever = RagRetriever(
        embedding_client=SimpleNamespace(embed=embed),
        retrieval_repository=SimpleNamespace(
            find_similar=find_similar,
        ),
        analysis_repository=SimpleNamespace(
            get_by_ids=get_by_ids,
        ),
        top_k=2,
    )

    contexts = asyncio.run(
        retriever.retrieve(
            normalized_report="report",
            server_id=1,
            monitoring_profile_id=None,
            command_set_hash=None,
            exclude_report_id=999,
        )
    )

    assert len(contexts) == 2
    assert [context.source_analysis_id for context in contexts] == [11, 12]
    assert len(retrieval_calls) == 1
    assert hydration_calls == [[11, 12]]
