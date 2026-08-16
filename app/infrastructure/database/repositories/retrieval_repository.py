"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.infrastructure.database.models.report_retrieval_document، app.infrastructure.database.session.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.report_retrieval_document import ReportRetrievalDocumentModel
from app.infrastructure.database.session import SessionLocal


class RetrievalRepository:
    """
    يمثل RetrievalRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

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

    def upsert_document(
        self,
        *,
        report_id: int,
        analysis_id: int,
        server_id: int,
        monitoring_profile_id: int | None,
        command_set_hash: str | None,
        connection_successful: bool | None,
        failed_command_ids: list[int],
        error_signatures: list[str],
        fingerprint: str,
        normalized_text: str,
        structured_features: dict,
        embedding: list[float],
        embedding_provider: str,
        embedding_model: str,
        embedding_dimensions: int,
        analysis_health_status: str | None,
    ) -> ReportRetrievalDocumentModel:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى upsert_document؛ المدخلات المهمة: report_id، analysis_id، server_id، monitoring_profile_id، command_set_hash، connection_successful.
        تعيد ReportRetrievalDocumentModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
            existing.monitoring_profile_id = monitoring_profile_id
            existing.command_set_hash = command_set_hash
            existing.connection_successful = connection_successful
            existing.failed_command_ids = failed_command_ids
            existing.error_signatures = error_signatures
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

    def clone_document(
        self,
        *,
        source_analysis_id: int,
        target_analysis_id: int,
        target_report_id: int,
        target_server_id: int,
        target_fingerprint: str,
        target_normalized_text: str,
        target_health_status: str | None,
    ) -> ReportRetrievalDocumentModel | None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى clone_document؛ المدخلات المهمة: source_analysis_id، target_analysis_id، target_report_id، target_server_id، target_fingerprint، target_normalized_text.
        تعيد ReportRetrievalDocumentModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            source = session.scalar(
                select(
                    ReportRetrievalDocumentModel
                ).where(
                    ReportRetrievalDocumentModel.analysis_id
                    == source_analysis_id
                )
            )

            if source is None:
                return None

            target = session.scalar(
                select(
                    ReportRetrievalDocumentModel
                ).where(
                    ReportRetrievalDocumentModel.analysis_id
                    == target_analysis_id
                )
            )

            if target is None:
                target = ReportRetrievalDocumentModel(
                    analysis_id=target_analysis_id
                )
                session.add(target)

            structured_features = dict(
                source.structured_features or {}
            )
            structured_features["health_status"] = (
                target_health_status
            )
            structured_features["analysis_source"] = "reused"
            structured_features["llm_called"] = False

            target.report_id = target_report_id
            target.server_id = target_server_id
            target.monitoring_profile_id = (
                source.monitoring_profile_id
            )
            target.command_set_hash = source.command_set_hash
            target.connection_successful = (
                source.connection_successful
            )
            target.failed_command_ids = list(
                source.failed_command_ids or []
            )
            target.error_signatures = list(
                source.error_signatures or []
            )
            target.fingerprint = target_fingerprint
            target.normalized_text = target_normalized_text
            target.structured_features = structured_features
            target.embedding = list(source.embedding)
            target.embedding_provider = source.embedding_provider
            target.embedding_model = source.embedding_model
            target.embedding_dimensions = (
                source.embedding_dimensions
            )
            target.analysis_health_status = (
                target_health_status
            )

            session.commit()
            session.refresh(target)

            return target

    def get_by_analysis_id(
        self,
        analysis_id: int,
    ) -> ReportRetrievalDocumentModel | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_analysis_id؛ المدخلات المهمة: analysis_id.
        تعيد ReportRetrievalDocumentModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            return session.scalar(
                select(
                    ReportRetrievalDocumentModel
                ).where(
                    ReportRetrievalDocumentModel.analysis_id
                    == analysis_id
                )
            )

    def find_by_full_text(
        self,
        *,
        query_text: str,
        server_id: int,
        monitoring_profile_id: int | None,
        command_set_hash: str | None,
        exclude_report_id: int | None = None,
        minimum_rank: float = 0.0,
        limit: int = 20,
    ):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى find_by_full_text؛ المدخلات المهمة: query_text، server_id، monitoring_profile_id، command_set_hash، exclude_report_id، minimum_rank.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        cleaned_query = query_text.strip()
        if not cleaned_query:
            return []

        query = func.plainto_tsquery(
            "simple",
            cleaned_query[:10_000],
        )
        rank = func.ts_rank_cd(
            ReportRetrievalDocumentModel.search_vector,
            query,
        ).label("rank")

        statement = (
            select(
                ReportRetrievalDocumentModel,
                rank,
            )
            .where(
                ReportRetrievalDocumentModel.server_id
                == server_id,
                ReportRetrievalDocumentModel.search_vector
                .op("@@")(query),
            )
            .order_by(rank.desc())
            .limit(limit)
        )

        if monitoring_profile_id is not None:
            statement = statement.where(
                ReportRetrievalDocumentModel
                .monitoring_profile_id
                == monitoring_profile_id
            )

        if command_set_hash:
            statement = statement.where(
                ReportRetrievalDocumentModel
                .command_set_hash
                == command_set_hash
            )

        if exclude_report_id is not None:
            statement = statement.where(
                ReportRetrievalDocumentModel.report_id
                != exclude_report_id
            )

        if minimum_rank > 0:
            statement = statement.where(
                rank >= minimum_rank
            )

        with self._session_factory() as session:
            rows = session.execute(statement).all()
            return [
                (document, float(value))
                for document, value in rows
            ]

    def find_similar(
        self,
        *,
        server_id: int,
        monitoring_profile_id: int | None,
        command_set_hash: str | None,
        embedding: list[float],
        exclude_report_id: int | None = None,
        minimum_score: float = 0.0,
        limit: int = 5,
        hnsw_ef_search: int = 100,
    ):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى find_similar؛ المدخلات المهمة: server_id، monitoring_profile_id، command_set_hash، embedding، exclude_report_id، minimum_score.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        distance = (
            ReportRetrievalDocumentModel.embedding.cosine_distance(
                embedding
            )
        )
        score = (1.0 - distance).label("score")

        maximum_distance = 1.0 - minimum_score

        statement = (
            select(
                ReportRetrievalDocumentModel,
                score,
            )
            .where(
                ReportRetrievalDocumentModel.server_id
                == server_id,
                distance <= maximum_distance,
            )
            .order_by(distance)
            .limit(limit)
        )

        if exclude_report_id is not None:
            statement = statement.where(
                ReportRetrievalDocumentModel.report_id
                != exclude_report_id
            )


        if monitoring_profile_id is not None:
            statement = statement.where(
                ReportRetrievalDocumentModel.monitoring_profile_id
                == monitoring_profile_id
            )

        if command_set_hash:
            statement = statement.where(
                ReportRetrievalDocumentModel.command_set_hash
                == command_set_hash
            )

        with self._session_factory() as session:
            session.execute(
                select(
                    func.set_config(
                        "hnsw.ef_search",
                        str(hnsw_ef_search),
                        True,
                    )
                )
            )

            rows = session.execute(statement).all()

            return [
                (document, float(value))
                for document, value in rows
            ]
