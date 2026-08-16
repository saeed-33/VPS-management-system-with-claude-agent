"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.infrastructure.database.models.knowledge_source، app.infrastructure.database.session، app.core.contracts.knowledge_sources، app.core.utils.datetime.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
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
    """
    يمثل KnowledgeSourceRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه application capabilities
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: session_factory.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._session_factory = session_factory

    def get_by_id(
        self,
        source_id: int,
    ) -> KnowledgeSourceModel | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_id؛ المدخلات المهمة: source_id.
        تعيد KnowledgeSourceModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            return session.get(
                KnowledgeSourceModel,
                source_id,
            )

    def get_by_slug(
        self,
        slug: str,
    ) -> KnowledgeSourceModel | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_slug؛ المدخلات المهمة: slug.
        تعيد KnowledgeSourceModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_all؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[KnowledgeSourceModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_enabled؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[KnowledgeSourceModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى create؛ المدخلات المهمة: data.
        تعيد KnowledgeSourceModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update؛ المدخلات المهمة: source_id، data.
        تعيد KnowledgeSourceModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى set_enabled؛ المدخلات المهمة: source_id، enabled.
        تعيد KnowledgeSourceModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى delete؛ المدخلات المهمة: source_id.
        تعيد bool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
