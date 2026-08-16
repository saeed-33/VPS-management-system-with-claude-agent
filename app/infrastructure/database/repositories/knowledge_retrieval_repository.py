"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.infrastructure.database.models.knowledge_document، app.infrastructure.database.models.knowledge_source، app.infrastructure.database.session.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import cast, func, or_, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.knowledge_document import (
    KnowledgeChunkModel,
    KnowledgeDocumentModel,
)
from app.infrastructure.database.models.knowledge_source import (
    KnowledgeSourceModel,
)
from app.infrastructure.database.session import SessionLocal


@dataclass(slots=True, frozen=True)
class KnowledgeSearchRow:
    """
    يمثل KnowledgeSearchRow مسؤولية محددة داخل طبقة Persistence infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه application capabilities
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    chunk_id: int
    document_id: int
    source_id: int
    source_slug: str
    source_name: str
    source_uri: str | None
    source_priority: int
    domains: tuple[str, ...]
    specialist_slugs: tuple[str, ...]
    document_title: str | None
    canonical_uri: str
    section_title: str | None
    page_number: int | None
    content: str
    score: float


class KnowledgeRetrievalRepository:
    """
    يمثل KnowledgeRetrievalRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

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

    def find_by_vector(
        self,
        *,
        query_embedding: list[float],
        specialist_slug: str | None,
        domains: tuple[str, ...],
        minimum_similarity: float,
        limit: int,
        hnsw_ef_search: int,
    ) -> list[KnowledgeSearchRow]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى find_by_vector؛ المدخلات المهمة: query_embedding، specialist_slug، domains، minimum_similarity، limit، hnsw_ef_search.
        تعيد list[KnowledgeSearchRow] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        similarity = (
            1.0
            - KnowledgeChunkModel.embedding.cosine_distance(
                query_embedding
            )
        ).label("score")

        statement = (
            select(
                KnowledgeChunkModel.id,
                KnowledgeChunkModel.document_id,
                KnowledgeChunkModel.source_id,
                KnowledgeSourceModel.slug,
                KnowledgeSourceModel.name,
                KnowledgeSourceModel.source_uri,
                KnowledgeSourceModel.priority,
                KnowledgeSourceModel.domains,
                KnowledgeSourceModel.specialist_slugs,
                KnowledgeDocumentModel.title,
                KnowledgeDocumentModel.canonical_uri,
                KnowledgeChunkModel.section_title,
                KnowledgeChunkModel.page_number,
                KnowledgeChunkModel.content,
                similarity,
            )
            .join(
                KnowledgeDocumentModel,
                KnowledgeDocumentModel.id
                == KnowledgeChunkModel.document_id,
            )
            .join(
                KnowledgeSourceModel,
                KnowledgeSourceModel.id
                == KnowledgeChunkModel.source_id,
            )
            .where(
                KnowledgeSourceModel.enabled.is_(True),
                KnowledgeDocumentModel.status == "indexed",
                KnowledgeChunkModel.embedding.is_not(None),
                similarity >= minimum_similarity,
                self._scope_condition(
                    specialist_slug=specialist_slug,
                    domains=domains,
                ),
            )
            .order_by(
                KnowledgeChunkModel.embedding.cosine_distance(
                    query_embedding
                )
            )
            .limit(limit)
        )

        with self._session_factory() as session:
            if hnsw_ef_search >= 10:
                session.execute(
                    text(
                        "SET LOCAL hnsw.ef_search = "
                        + str(int(hnsw_ef_search))
                    )
                )
            rows = session.execute(statement).all()

        return [self._to_row(row) for row in rows]

    def find_by_full_text(
        self,
        *,
        query_text: str,
        specialist_slug: str | None,
        domains: tuple[str, ...],
        limit: int,
    ) -> list[KnowledgeSearchRow]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى find_by_full_text؛ المدخلات المهمة: query_text، specialist_slug، domains، limit.
        تعيد list[KnowledgeSearchRow] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        query_text = query_text.strip()
        if not query_text:
            return []

        ts_query = func.websearch_to_tsquery(
            "simple",
            query_text,
        )
        rank = func.ts_rank_cd(
            KnowledgeChunkModel.search_vector,
            ts_query,
        ).label("score")

        statement = (
            select(
                KnowledgeChunkModel.id,
                KnowledgeChunkModel.document_id,
                KnowledgeChunkModel.source_id,
                KnowledgeSourceModel.slug,
                KnowledgeSourceModel.name,
                KnowledgeSourceModel.source_uri,
                KnowledgeSourceModel.priority,
                KnowledgeSourceModel.domains,
                KnowledgeSourceModel.specialist_slugs,
                KnowledgeDocumentModel.title,
                KnowledgeDocumentModel.canonical_uri,
                KnowledgeChunkModel.section_title,
                KnowledgeChunkModel.page_number,
                KnowledgeChunkModel.content,
                rank,
            )
            .join(
                KnowledgeDocumentModel,
                KnowledgeDocumentModel.id
                == KnowledgeChunkModel.document_id,
            )
            .join(
                KnowledgeSourceModel,
                KnowledgeSourceModel.id
                == KnowledgeChunkModel.source_id,
            )
            .where(
                KnowledgeSourceModel.enabled.is_(True),
                KnowledgeDocumentModel.status == "indexed",
                KnowledgeChunkModel.search_vector.op("@@")(
                    ts_query
                ),
                self._scope_condition(
                    specialist_slug=specialist_slug,
                    domains=domains,
                ),
            )
            .order_by(
                rank.desc(),
                KnowledgeSourceModel.priority,
                KnowledgeChunkModel.id,
            )
            .limit(limit)
        )

        with self._session_factory() as session:
            rows = session.execute(statement).all()

        return [self._to_row(row) for row in rows]

    @staticmethod
    def _scope_condition(
        *,
        specialist_slug: str | None,
        domains: tuple[str, ...],
    ):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى _scope_condition؛ المدخلات المهمة: specialist_slug، domains.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        conditions = []

        specialist_json = cast(
            KnowledgeSourceModel.specialist_slugs,
            JSONB,
        )
        domains_json = cast(
            KnowledgeSourceModel.domains,
            JSONB,
        )

        if specialist_slug:
            conditions.append(
                specialist_json.contains(
                    [specialist_slug]
                )
            )

        for domain in domains:
            conditions.append(
                domains_json.contains([domain])
            )

        if not conditions:
            return text("TRUE")

        return or_(*conditions)

    @staticmethod
    def _to_row(row) -> KnowledgeSearchRow:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى _to_row؛ المدخلات المهمة: row.
        تعيد KnowledgeSearchRow أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return KnowledgeSearchRow(
            chunk_id=row[0],
            document_id=row[1],
            source_id=row[2],
            source_slug=row[3],
            source_name=row[4],
            source_uri=row[5],
            source_priority=row[6],
            domains=tuple(
                str(value).casefold()
                for value in (row[7] or [])
            ),
            specialist_slugs=tuple(
                str(value).casefold()
                for value in (row[8] or [])
            ),
            document_title=row[9],
            canonical_uri=row[10],
            section_title=row[11],
            page_number=row[12],
            content=row[13],
            score=float(row[14] or 0.0),
        )
