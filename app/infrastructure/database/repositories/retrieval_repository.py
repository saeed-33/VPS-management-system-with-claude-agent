"""
فهرس التقارير المستخدم للبحث النصي والتشابه وإعادة استخدام سياق سابق.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.report_retrieval_document import ReportRetrievalDocumentModel
from app.infrastructure.database.session import SessionLocal


class RetrievalRepository:
    """
    مسؤول عن فهرسة التقارير واسترجاع الحالات النصية والمشابهة.
    """
    def __init__(self, session_factory: sessionmaker = SessionLocal) -> None:
        """
        يهيئ مستودع فهرس التقارير المستخدم للبحث النصي والتشابه وإعادة استخدام سياق سابق بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
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
        ينشئ أو يحدث سجلًا في فهرس التقارير المستخدم للبحث النصي والتشابه وإعادة استخدام سياق سابق ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
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
        ينسخ سجلًا من فهرس التقارير المستخدم للبحث النصي والتشابه وإعادة استخدام سياق سابق إلى سياق جديد مع الحفاظ على مرجعه القابل للتتبع.
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
        يسترجع سجلًا من فهرس التقارير المستخدم للبحث النصي والتشابه وإعادة استخدام سياق سابق بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
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
        يبحث داخل فهرس التقارير المستخدم للبحث النصي والتشابه وإعادة استخدام سياق سابق عن سجلات تطابق الحالة أو البصمة أو الشروط المقدمة.
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
        يبحث داخل فهرس التقارير المستخدم للبحث النصي والتشابه وإعادة استخدام سياق سابق عن سجلات تطابق الحالة أو البصمة أو الشروط المقدمة.
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
