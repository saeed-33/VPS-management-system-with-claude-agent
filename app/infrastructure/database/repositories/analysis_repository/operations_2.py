"""
تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء.
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.report_analysis.status import AnalysisJobStatus
from app.infrastructure.database.models.report_analysis.analysis import ReportAnalysisModel
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.analysis.analysis_issue import AnalysisIssue
from app.core.contracts.analysis.report_analysis_result import ReportAnalysisResult
from app.core.policies.error_classification import classify_issue, classify_result
from app.core.utils.datetime import utc_now


class _AnalysisRepositoryMixin2:
    """ينظم مجموعة من عمليات المستودع."""

    def list_pending_or_running(
        self,
    ) -> list[ReportAnalysisModel]:
        """
        يعرض قائمة مرتبة من تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = (
                select(ReportAnalysisModel)
                .where(
                    ReportAnalysisModel.status.in_(
                        [
                            AnalysisJobStatus.PENDING.value,
                            AnalysisJobStatus.RUNNING.value,
                        ]
                    )
                )
                .order_by(
                    ReportAnalysisModel.created_at
                )
            )

            return list(
                session.scalars(statement).all()
            )

    def find_completed_by_fingerprint(
        self,
        *,
        server_id: int,
        report_fingerprint: str,
        exclude_report_id: int | None = None,
    ) -> ReportAnalysisModel | None:
        """
        يبحث داخل تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء عن سجلات تطابق الحالة أو البصمة أو الشروط المقدمة.
        """
        with self._session_factory() as session:
            statement = (
                select(ReportAnalysisModel)
                .where(
                    ReportAnalysisModel.server_id
                    == server_id,
                    ReportAnalysisModel.report_fingerprint
                    == report_fingerprint,
                    ReportAnalysisModel.status
                    == AnalysisJobStatus.COMPLETED.value,
                    ReportAnalysisModel.health_status
                    .is_not(None),
                )
                .order_by(
                    ReportAnalysisModel.finished_at.desc(),
                    ReportAnalysisModel.id.desc(),
                )
            )

            if exclude_report_id is not None:
                statement = statement.where(
                    ReportAnalysisModel.report_id
                    != exclude_report_id
                )

            return session.scalar(
                statement.limit(1)
            )

    def update_retrieval_metadata(
        self,
        *,
        analysis_id: int,
        report_fingerprint: str,
        normalized_report: str,
        analysis_source: str = "generated",
        reused_from_analysis_id: int | None = None,
        retrieval_strategy: str | None = None,
        retrieval_score: float | None = None,
        llm_called: bool = True,
    ) -> None:
        """
        يحدّث انتقالًا أو إعدادًا في تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                raise ValueError(
                    f"Analysis {analysis_id} was not found."
                )

            model.report_fingerprint = (
                report_fingerprint
            )

            model.normalized_report = (
                normalized_report
            )

            model.analysis_source = analysis_source

            model.reused_from_analysis_id = (
                reused_from_analysis_id
            )

            model.retrieval_strategy = (
                retrieval_strategy
            )

            model.retrieval_score = retrieval_score
            model.llm_called = llm_called
            model.updated_at = utc_now()

            session.commit()

    def update_performance_metrics(
        self,
        *,
        analysis_id: int,
        performance_metrics: dict,
    ) -> None:
        """
        يحدّث انتقالًا أو إعدادًا في تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                raise ValueError(
                    f"Analysis {analysis_id} was not found."
                )

            model.performance_metrics = performance_metrics
            model.updated_at = utc_now()

            session.commit()

    def create_reused_analysis(
        self,
        *,
        report_id: int,
        server_id: int,
        source_analysis: ReportAnalysisModel,
        report_fingerprint: str,
        normalized_report: str,
    ) -> ReportAnalysisModel:
        """
        ينشئ أو يحدث سجلًا في تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        now = utc_now()

        model = ReportAnalysisModel(
            report_id=report_id,
            server_id=server_id,
            provider_name=(
                source_analysis.provider_name
            ),
            model_name=source_analysis.model_name,
            status=AnalysisJobStatus.COMPLETED.value,
            health_status=(
                source_analysis.health_status
            ),
            summary=source_analysis.summary,
            issues=[
                (
                    parsed := AnalysisIssue.model_validate(issue)
                ).model_copy(
                    update={"classification": classify_issue(parsed)}
                ).model_dump(mode="json")
                for issue in (source_analysis.issues or [])
            ],
            positive_findings=list(
                source_analysis.positive_findings
                or []
            ),
            recommended_actions=list(
                source_analysis.recommended_actions
                or []
            ),
            analysis_error=None,
            started_at=now,
            finished_at=now,
            duration_ms=0.0,
            attempts=0,
            report_fingerprint=(
                report_fingerprint
            ),
            normalized_report=(
                normalized_report
            ),
            analysis_source="reused",
            reused_from_analysis_id=(
                source_analysis.id
            ),
            retrieval_strategy=(
                "exact_fingerprint"
            ),
            retrieval_score=1.0,
            llm_called=False,
        )

        with self._session_factory() as session:
            session.add(model)

            try:
                session.commit()

            except IntegrityError:
                session.rollback()

                existing = session.scalar(
                    select(
                        ReportAnalysisModel
                    ).where(
                        ReportAnalysisModel.report_id
                        == report_id
                    )
                )

                if existing is None:
                    raise

                return existing

            session.refresh(model)

            return model
