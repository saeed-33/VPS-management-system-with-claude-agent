from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.shared.database.models.report_retrieval_document import ReportRetrievalDocumentModel
from app.shared.database.session import SessionLocal


class RetrievalRepository:
    def __init__(self, session_factory: sessionmaker = SessionLocal) -> None:
        self._session_factory = session_factory

    def upsert_document(self, *, report_id: int, analysis_id: int, server_id: int, fingerprint: str, normalized_text: str, structured_features: dict, embedding: list[float], embedding_provider: str, embedding_model: str, embedding_dimensions: int, analysis_health_status: str | None) -> ReportRetrievalDocumentModel:
        with self._session_factory() as session:
            existing = session.scalar(
                select(ReportRetrievalDocumentModel).where(
                    ReportRetrievalDocumentModel.analysis_id == analysis_id
                )
            )
            if existing is None:
                existing = ReportRetrievalDocumentModel(analysis_id=analysis_id)
                session.add(existing)

            existing.report_id = report_id
            existing.server_id = server_id
            existing.fingerprint = fingerprint
            existing.normalized_text = normalized_text
            existing.structured_features = structured_features
            existing.embedding = embedding
            existing.embedding_provider = embedding_provider
            existing.embedding_model = embedding_model
            existing.embedding_dimensions = embedding_dimensions
            existing.analysis_health_status = analysis_health_status
            session.commit()
            session.refresh(existing)
            return existing

    def find_similar(self, *, server_id: int, embedding: list[float], limit: int = 5) -> list[tuple[ReportRetrievalDocumentModel, float]]:
        distance = ReportRetrievalDocumentModel.embedding.cosine_distance(embedding)
        statement = (
            select(ReportRetrievalDocumentModel, (1.0 - distance).label("score"))
            .where(ReportRetrievalDocumentModel.server_id == server_id)
            .order_by(distance)
            .limit(limit)
        )
        with self._session_factory() as session:
            return [(document, float(score)) for document, score in session.execute(statement).all()]
