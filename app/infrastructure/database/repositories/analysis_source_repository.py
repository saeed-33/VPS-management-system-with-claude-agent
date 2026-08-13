from sqlalchemy import delete, select
from sqlalchemy.orm import sessionmaker

from app.shared.database.models.report_analysis_source import (
    ReportAnalysisSourceModel,
)
from app.infrastructure.database.session import SessionLocal


class AnalysisSourceRepository:
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        self._session_factory = session_factory

    def replace_for_analysis(
        self,
        *,
        analysis_id: int,
        sources: list[dict],
    ) -> None:
        with self._session_factory() as session:
            session.execute(
                delete(ReportAnalysisSourceModel).where(
                    ReportAnalysisSourceModel.analysis_id
                    == analysis_id
                )
            )
            for source in sources:
                session.add(
                    ReportAnalysisSourceModel(
                        analysis_id=analysis_id,
                        **source,
                    )
                )
            session.commit()

    def list_by_analysis_id(
        self,
        analysis_id: int,
    ) -> list[ReportAnalysisSourceModel]:
        with self._session_factory() as session:
            statement = (
                select(ReportAnalysisSourceModel)
                .where(
                    ReportAnalysisSourceModel.analysis_id
                    == analysis_id
                )
                .order_by(
                    ReportAnalysisSourceModel.rank.asc()
                    .nulls_first(),
                    ReportAnalysisSourceModel.id.asc(),
                )
            )
            return list(
                session.scalars(statement).all()
            )
