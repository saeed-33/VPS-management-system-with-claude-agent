from __future__ import annotations

from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.knowledge_source import (
    KnowledgeSourceModel,
)
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.knowledge_sources import (
    CreateKnowledgeSourceDTO,
    UpdateKnowledgeSourceDTO,
)
from app.core.utils.datetime import utc_now


class KnowledgeSourceRepository:
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        self._session_factory = session_factory

    def get_by_id(
        self,
        source_id: int,
    ) -> KnowledgeSourceModel | None:
        with self._session_factory() as session:
            return session.get(
                KnowledgeSourceModel,
                source_id,
            )

    def get_by_slug(
        self,
        slug: str,
    ) -> KnowledgeSourceModel | None:
        with self._session_factory() as session:
            return session.scalar(
                select(KnowledgeSourceModel)
                .where(
                    KnowledgeSourceModel.slug
                    == slug.strip().lower()
                )
            )

    def list_all(
        self,
    ) -> list[KnowledgeSourceModel]:
        with self._session_factory() as session:
            return list(
                session.scalars(
                    select(KnowledgeSourceModel)
                    .order_by(
                        KnowledgeSourceModel.priority,
                        KnowledgeSourceModel.name,
                        KnowledgeSourceModel.id,
                    )
                ).all()
            )

    def list_enabled(
        self,
    ) -> list[KnowledgeSourceModel]:
        with self._session_factory() as session:
            return list(
                session.scalars(
                    select(KnowledgeSourceModel)
                    .where(
                        KnowledgeSourceModel.enabled
                        .is_(True)
                    )
                    .order_by(
                        KnowledgeSourceModel.priority,
                        KnowledgeSourceModel.name,
                        KnowledgeSourceModel.id,
                    )
                ).all()
            )

    def create(
        self,
        data: CreateKnowledgeSourceDTO,
    ) -> KnowledgeSourceModel:
        model = KnowledgeSourceModel(
            slug=data.slug,
            name=data.name,
            description=(
                data.description.strip()
                if data.description
                else data.description
            ),
            source_type=data.source_type,
            source_uri=data.source_uri,
            inline_content=data.inline_content,
            enabled=data.enabled,
            domains=list(data.domains),
            specialist_slugs=list(
                data.specialist_slugs
            ),
            tags=list(data.tags),
            priority=data.priority,
            source_metadata=dict(data.metadata),
        )

        with self._session_factory() as session:
            session.add(model)

            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError(
                    "Knowledge source slug already exists."
                )

            session.refresh(model)
            return model

    def update(
        self,
        source_id: int,
        data: UpdateKnowledgeSourceDTO,
    ) -> KnowledgeSourceModel | None:
        with self._session_factory() as session:
            model = session.get(
                KnowledgeSourceModel,
                source_id,
            )

            if model is None:
                return None

            values = {
                key: value
                for key, value
                in asdict(data).items()
                if value is not None
            }

            metadata = values.pop(
                "metadata",
                None,
            )

            for key, value in values.items():
                if key in {
                    "domains",
                    "specialist_slugs",
                    "tags",
                }:
                    value = list(value)

                setattr(
                    model,
                    key,
                    value,
                )

            if metadata is not None:
                model.source_metadata = dict(
                    metadata
                )

            model.updated_at = utc_now()
            session.commit()
            session.refresh(model)
            return model

    def set_enabled(
        self,
        source_id: int,
        enabled: bool,
    ) -> KnowledgeSourceModel | None:
        with self._session_factory() as session:
            model = session.get(
                KnowledgeSourceModel,
                source_id,
            )

            if model is None:
                return None

            model.enabled = enabled
            model.updated_at = utc_now()
            session.commit()
            session.refresh(model)
            return model

    def delete(
        self,
        source_id: int,
    ) -> bool:
        with self._session_factory() as session:
            model = session.get(
                KnowledgeSourceModel,
                source_id,
            )

            if model is None:
                return False

            session.delete(model)
            session.commit()
            return True
