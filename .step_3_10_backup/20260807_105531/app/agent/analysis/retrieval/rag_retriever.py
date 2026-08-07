import logging

from app.agent.analysis.retrieval.embedding_client import EmbeddingClient
from app.agent.analysis.retrieval.rag_context import RetrievedAnalysisContext
from app.shared.database.repositories.analysis_repository import AnalysisRepository
from app.shared.database.repositories.retrieval_repository import RetrievalRepository

logger = logging.getLogger(__name__)


class RagRetriever:
    def __init__(
        self,
        *,
        embedding_client: EmbeddingClient,
        retrieval_repository: RetrievalRepository,
        analysis_repository: AnalysisRepository,
        top_k: int = 3,
        minimum_score: float = 0.72,
        hnsw_ef_search: int = 100,
    ) -> None:
        self._embedding_client = embedding_client
        self._retrieval_repository = retrieval_repository
        self._analysis_repository = analysis_repository
        self._top_k = top_k
        self._minimum_score = minimum_score
        self._hnsw_ef_search = hnsw_ef_search

    async def retrieve(
        self,
        *,
        normalized_report: str,
        server_id: int,
        monitoring_profile_id: int | None,
        command_set_hash: str | None,
        exclude_report_id: int,
    ) -> list[RetrievedAnalysisContext]:
        embedding = await self._embedding_client.embed(
            normalized_report
        )

        candidates = self._retrieval_repository.find_similar(
            server_id=server_id,
            monitoring_profile_id=monitoring_profile_id,
            command_set_hash=command_set_hash,
            embedding=embedding,
            exclude_report_id=exclude_report_id,
            minimum_score=self._minimum_score,
            limit=self._top_k,
            hnsw_ef_search=self._hnsw_ef_search,
        )

        contexts: list[RetrievedAnalysisContext] = []

        for rank, (document, score) in enumerate(
            candidates,
            start=1,
        ):
            analysis = self._analysis_repository.get_by_id(
                document.analysis_id
            )
            if analysis is None or analysis.status != "completed":
                continue

            contexts.append(
                RetrievedAnalysisContext(
                    source_report_id=document.report_id,
                    source_analysis_id=document.analysis_id,
                    score=score,
                    rank=rank,
                    health_status=analysis.health_status,
                    summary=analysis.summary,
                    issues=list(analysis.issues or []),
                    positive_findings=list(
                        analysis.positive_findings or []
                    ),
                    recommended_actions=list(
                        analysis.recommended_actions or []
                    ),
                )
            )

        logger.info(
            "RAG retrieval completed | server_id=%s | "
            "exclude_report_id=%s | contexts=%s",
            server_id,
            exclude_report_id,
            len(contexts),
        )
        return contexts
