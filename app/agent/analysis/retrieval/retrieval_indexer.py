import json
import logging

from app.agent.analysis.retrieval.embedding_client import EmbeddingClient
from app.shared.database.repositories.analysis_repository import AnalysisRepository
from app.shared.database.repositories.retrieval_repository import RetrievalRepository

logger = logging.getLogger(__name__)


class RetrievalIndexer:
    def __init__(self, *, analysis_repository: AnalysisRepository, retrieval_repository: RetrievalRepository, embedding_client: EmbeddingClient) -> None:
        self._analysis_repository = analysis_repository
        self._retrieval_repository = retrieval_repository
        self._embedding_client = embedding_client

    async def index_analysis(self, analysis_id: int) -> None:
        analysis = self._analysis_repository.get_by_id(analysis_id)
        if analysis is None:
            raise ValueError(f"Analysis {analysis_id} was not found.")
        if analysis.status != "completed":
            raise ValueError(f"Analysis {analysis_id} is not completed.")
        if not analysis.report_fingerprint or not analysis.normalized_report:
            raise ValueError(f"Analysis {analysis_id} has no retrieval metadata.")

        embedding = await self._embedding_client.embed(analysis.normalized_report)
        features = {
            "health_status": analysis.health_status,
            "analysis_source": analysis.analysis_source,
            "llm_called": analysis.llm_called,
        }
        self._retrieval_repository.upsert_document(
            report_id=analysis.report_id, analysis_id=analysis.id, server_id=analysis.server_id,
            fingerprint=analysis.report_fingerprint, normalized_text=analysis.normalized_report,
            structured_features=features, embedding=embedding,
            embedding_provider=self._embedding_client.provider_name,
            embedding_model=self._embedding_client.model_name,
            embedding_dimensions=self._embedding_client.dimensions,
            analysis_health_status=analysis.health_status,
        )
        logger.info("Analysis retrieval document indexed | analysis_id=%s", analysis_id)
