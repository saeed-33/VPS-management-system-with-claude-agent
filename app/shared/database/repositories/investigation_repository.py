from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.shared.database.models.investigation import (
    InvestigationModel,
    InvestigationSpecialistCandidateModel,
)
from app.shared.database.session import SessionLocal
from app.shared.dto.investigations import PersistInvestigationDTO


class InvestigationRepository:
    def __init__(self, session_factory: sessionmaker = SessionLocal) -> None:
        self._session_factory = session_factory

    def create(self, data: PersistInvestigationDTO) -> InvestigationModel:
        model = InvestigationModel(
            investigation_id=data.investigation_id,
            server_id=data.server_id,
            report_id=data.report_id,
            analysis_id=data.analysis_id,
            status=data.status,
            should_investigate=data.should_investigate,
            routing_reasons=list(data.routing_reasons),
            detected_domains=list(data.detected_domains),
            unmatched_issue_indexes=list(data.unmatched_issue_indexes),
            registry_size=data.registry_size,
            candidate_limit=data.candidate_limit,
            selection_limit=data.selection_limit,
            max_specialists=data.max_specialists,
            max_rounds=data.max_rounds,
            max_actions=data.max_actions,
            routing_version=data.routing_version,
            investigation_metadata=dict(data.metadata),
        )
        model.candidates = [
            InvestigationSpecialistCandidateModel(
                specialist_definition_id=item.specialist_definition_id,
                specialist_slug=item.specialist_slug,
                specialist_name=item.specialist_name,
                score=item.score,
                priority=item.priority,
                candidate_rank=item.candidate_rank,
                is_selected=item.is_selected,
                selected_rank=item.selected_rank,
                matched_domains=list(item.matched_domains),
                matched_trigger_hints=list(item.matched_trigger_hints),
                matched_issue_indexes=list(item.matched_issue_indexes),
            )
            for item in data.candidates
        ]

        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            _ = model.candidates
            return model

    def update_runtime_snapshot(
        self,
        *,
        investigation_id: str,
        status: str,
        metadata: dict,
    ) -> InvestigationModel:
        with self._session_factory() as session:
            model = session.scalar(
                select(
                    InvestigationModel
                ).where(
                    InvestigationModel
                    .investigation_id
                    == investigation_id
                )
            )

            if model is None:
                raise ValueError(
                    "Investigation not found: "
                    f"{investigation_id}"
                )

            model.status = status

            model.investigation_metadata = (
                dict(metadata)
            )

            session.add(
                model
            )

            session.commit()

            session.refresh(
                model
            )

            _ = model.candidates

            return model

    def get_by_investigation_id(
        self,
        investigation_id: str,
    ) -> InvestigationModel | None:
        with self._session_factory() as session:
            model = session.scalar(
                select(InvestigationModel).where(
                    InvestigationModel.investigation_id == investigation_id
                )
            )
            if model is not None:
                _ = model.candidates
            return model

    def list_recent(
        self,
        *,
        limit: int = 100,
        server_id: int | None = None,
    ) -> list[InvestigationModel]:
        if limit < 1:
            raise ValueError("limit must be >= 1.")

        statement = (
            select(InvestigationModel)
            .order_by(
                InvestigationModel.created_at.desc(),
                InvestigationModel.id.desc(),
            )
            .limit(limit)
        )

        if server_id is not None:
            statement = statement.where(
                InvestigationModel.server_id == server_id
            )

        with self._session_factory() as session:
            models = list(
                session.scalars(statement).all()
            )
            for model in models:
                _ = model.candidates
            return models

    def list_by_report_id(self, report_id: int) -> list[InvestigationModel]:
        with self._session_factory() as session:
            models = list(
                session.scalars(
                    select(InvestigationModel)
                    .where(InvestigationModel.report_id == report_id)
                    .order_by(
                        InvestigationModel.created_at.desc(),
                        InvestigationModel.id.desc(),
                    )
                ).all()
            )
            for model in models:
                _ = model.candidates
            return models
