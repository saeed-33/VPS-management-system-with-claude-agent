"""
تعريفات المتخصصين ومجالاتهم وأدواتهم وحدود تحقيقهم.
"""
from __future__ import annotations

from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.specialist_definition import SpecialistDefinitionModel
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.specialists import CreateSpecialistDefinitionDTO, UpdateSpecialistDefinitionDTO
from app.core.utils.datetime import utc_now

_LIST_FIELDS = {"domains", "trigger_hints", "knowledge_topics", "allowed_tool_ids"}


def _normalize_string_list(values: list[str]) -> list[str]:
    """
    يوحد قيمة مساعدة قبل استخدامها في تعريفات المتخصصين ومجالاتهم وأدواتهم وحدود تحقيقهم.
    """
    result = []
    seen = set()
    for raw in values:
        value = raw.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


class SpecialistDefinitionRepository:
    """
    مسؤول عن تعريف المتخصصين وتفعيلهم وتحديث حدودهم وأدواتهم.
    """
    def __init__(self, session_factory: sessionmaker = SessionLocal) -> None:
        """
        يهيئ مستودع تعريفات المتخصصين ومجالاتهم وأدواتهم وحدود تحقيقهم بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
        """
        self._session_factory = session_factory

    def get_by_id(self, specialist_id: int) -> SpecialistDefinitionModel | None:
        """
        يسترجع سجلًا من تعريفات المتخصصين ومجالاتهم وأدواتهم وحدود تحقيقهم بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.get(SpecialistDefinitionModel, specialist_id)

    def get_by_slug(self, slug: str) -> SpecialistDefinitionModel | None:
        """
        يسترجع سجلًا من تعريفات المتخصصين ومجالاتهم وأدواتهم وحدود تحقيقهم بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.scalar(
                select(SpecialistDefinitionModel).where(
                    SpecialistDefinitionModel.slug == slug.strip().lower()
                )
            )

    def list_all(self) -> list[SpecialistDefinitionModel]:
        """
        يعرض قائمة مرتبة من تعريفات المتخصصين ومجالاتهم وأدواتهم وحدود تحقيقهم مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = select(SpecialistDefinitionModel).order_by(
                SpecialistDefinitionModel.priority,
                SpecialistDefinitionModel.name,
                SpecialistDefinitionModel.id,
            )
            return list(session.scalars(statement).all())

    def list_enabled(self) -> list[SpecialistDefinitionModel]:
        """
        يعرض قائمة مرتبة من تعريفات المتخصصين ومجالاتهم وأدواتهم وحدود تحقيقهم مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = (
                select(SpecialistDefinitionModel)
                .where(SpecialistDefinitionModel.enabled.is_(True))
                .order_by(
                    SpecialistDefinitionModel.priority,
                    SpecialistDefinitionModel.name,
                    SpecialistDefinitionModel.id,
                )
            )
            return list(session.scalars(statement).all())

    def create(self, data: CreateSpecialistDefinitionDTO) -> SpecialistDefinitionModel:
        """
        ينشئ أو يحدث سجلًا في تعريفات المتخصصين ومجالاتهم وأدواتهم وحدود تحقيقهم ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = SpecialistDefinitionModel(
            slug=data.slug.strip().lower(),
            name=data.name.strip(),
            description=data.description.strip() if data.description else data.description,
            instructions=data.instructions.strip() if data.instructions else data.instructions,
            enabled=data.enabled,
            domains=_normalize_string_list(data.domains),
            trigger_hints=_normalize_string_list(data.trigger_hints),
            knowledge_topics=_normalize_string_list(data.knowledge_topics),
            allowed_tool_ids=_normalize_string_list(data.allowed_tool_ids),
            priority=data.priority,
            max_rounds=data.max_rounds,
            max_actions=data.max_actions,
            specialist_metadata=dict(data.metadata),
        )
        with self._session_factory() as session:
            session.add(model)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError("Specialist slug already exists.")
            session.refresh(model)
            return model

    def update(self, specialist_id: int, data: UpdateSpecialistDefinitionDTO) -> SpecialistDefinitionModel | None:
        """
        يحدّث انتقالًا أو إعدادًا في تعريفات المتخصصين ومجالاتهم وأدواتهم وحدود تحقيقهم دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.get(SpecialistDefinitionModel, specialist_id)
            if model is None:
                return None

            values = {k: v for k, v in asdict(data).items() if v is not None}
            metadata_value = values.pop("metadata", None)

            for key, value in values.items():
                if key in _LIST_FIELDS:
                    value = _normalize_string_list(value)
                elif isinstance(value, str):
                    value = value.strip()
                setattr(model, key, value)

            if metadata_value is not None:
                model.specialist_metadata = dict(metadata_value)

            model.updated_at = utc_now()
            session.commit()
            session.refresh(model)
            return model

    def set_enabled(self, specialist_id: int, enabled: bool) -> SpecialistDefinitionModel | None:
        """
        يحدّث انتقالًا أو إعدادًا في تعريفات المتخصصين ومجالاتهم وأدواتهم وحدود تحقيقهم دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.get(SpecialistDefinitionModel, specialist_id)
            if model is None:
                return None
            model.enabled = enabled
            model.updated_at = utc_now()
            session.commit()
            session.refresh(model)
            return model

    def delete(self, specialist_id: int) -> bool:
        """
        يزيل ارتباطًا أو سجلًا من تعريفات المتخصصين ومجالاتهم وأدواتهم وحدود تحقيقهم بعد تطبيق قواعد الملكية المطلوبة.
        """
        with self._session_factory() as session:
            model = session.get(SpecialistDefinitionModel, specialist_id)
            if model is None:
                return False
            session.delete(model)
            session.commit()
            return True
