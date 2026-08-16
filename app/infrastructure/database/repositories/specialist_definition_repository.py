"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.infrastructure.database.models.specialist_definition، app.infrastructure.database.session، app.core.contracts.specialists، app.core.utils.datetime.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

    تُستدعى عندما يصل workflow إلى _normalize_string_list؛ المدخلات المهمة: values.
    تعيد list[str] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يمثل SpecialistDefinitionRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه application capabilities
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, session_factory: sessionmaker = SessionLocal) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: session_factory.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._session_factory = session_factory

    def get_by_id(self, specialist_id: int) -> SpecialistDefinitionModel | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_id؛ المدخلات المهمة: specialist_id.
        تعيد SpecialistDefinitionModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            return session.get(SpecialistDefinitionModel, specialist_id)

    def get_by_slug(self, slug: str) -> SpecialistDefinitionModel | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_slug؛ المدخلات المهمة: slug.
        تعيد SpecialistDefinitionModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            return session.scalar(
                select(SpecialistDefinitionModel).where(
                    SpecialistDefinitionModel.slug == slug.strip().lower()
                )
            )

    def list_all(self) -> list[SpecialistDefinitionModel]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_all؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[SpecialistDefinitionModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_enabled؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[SpecialistDefinitionModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى create؛ المدخلات المهمة: data.
        تعيد SpecialistDefinitionModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update؛ المدخلات المهمة: specialist_id، data.
        تعيد SpecialistDefinitionModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى set_enabled؛ المدخلات المهمة: specialist_id، enabled.
        تعيد SpecialistDefinitionModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى delete؛ المدخلات المهمة: specialist_id.
        تعيد bool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            model = session.get(SpecialistDefinitionModel, specialist_id)
            if model is None:
                return False
            session.delete(model)
            session.commit()
            return True
