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


class _AnalysisQueriesMixin:
    """ينظم مجموعة من عمليات المستودع."""

    def get_by_id(
        self,
        analysis_id: int,
    ) -> ReportAnalysisModel | None:
        """
        يسترجع سجلًا من تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.get(
                ReportAnalysisModel,
                analysis_id,
            )

    def get_by_report_id(
        self,
        report_id: int,
    ) -> ReportAnalysisModel | None:
        """
        يسترجع سجلًا من تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            statement = select(
                ReportAnalysisModel
            ).where(
                ReportAnalysisModel.report_id
                == report_id
            )

            return session.scalar(statement)

    def create_pending(
        self,
        *,
        report_id: int,
        server_id: int,
        provider_name: str,
        model_name: str,
    ) -> ReportAnalysisModel:
        """
        ينشئ أو يحدث سجلًا في تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = ReportAnalysisModel(
            report_id=report_id,
            server_id=server_id,
            provider_name=provider_name,
            model_name=model_name,
            status=AnalysisJobStatus.PENDING.value,
        )

        with self._session_factory() as session:
            session.add(model)

            try:
                session.commit()
            except IntegrityError:
                session.rollback()

                existing = session.scalar(
                    select(ReportAnalysisModel).where(
                        ReportAnalysisModel.report_id
                        == report_id
                    )
                )

                if existing is None:
                    raise

                return existing

            session.refresh(model)

            return model

    def mark_running(
        self,
        analysis_id: int,
    ) -> None:
        """
        ينقل سجلًا من تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء إلى حالة تشغيلية جديدة مع حفظ سبب الانتقال.
        """
        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                raise ValueError(
                    f"Analysis {analysis_id} not found."
                )

            model.status = (
                AnalysisJobStatus.RUNNING.value
            )

            model.started_at = utc_now()
            model.finished_at = None
            model.analysis_error = None
            model.attempts += 1
            model.updated_at = utc_now()

            session.commit()

    def mark_completed(
        self,
        *,
        analysis_id: int,
        result: ReportAnalysisResult,
        finished_at: datetime,
        duration_ms: float,
    ) -> None:
        """
        ينقل سجلًا من تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء إلى حالة تشغيلية جديدة مع حفظ سبب الانتقال.
        """
        result = classify_result(result)

        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                raise ValueError(
                    f"Analysis {analysis_id} not found."
                )

            model.status = (
                AnalysisJobStatus.COMPLETED.value
            )

            model.health_status = (
                result.health_status.value
            )

            model.summary = result.summary

            model.issues = [
                issue.model_dump(
                    mode="json"
                )
                for issue in result.issues
            ]

            model.positive_findings = (
                result.positive_findings
            )

            model.recommended_actions = (
                result.recommended_actions
            )

            model.analysis_error = None
            model.finished_at = finished_at
            model.duration_ms = duration_ms
            model.updated_at = utc_now()

            session.commit()

    def mark_failed(
        self,
        *,
        analysis_id: int,
        error_message: str,
        finished_at: datetime,
        duration_ms: float,
    ) -> None:
        """
        ينقل سجلًا من تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء إلى حالة تشغيلية جديدة مع حفظ سبب الانتقال.
        """
        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                return

            model.status = (
                AnalysisJobStatus.FAILED.value
            )

            model.analysis_error = error_message
            model.finished_at = finished_at
            model.duration_ms = duration_ms
            model.updated_at = utc_now()

            session.commit()

    def reset_for_retry(
        self,
        analysis_id: int,
    ) -> None:
        """
        يعيد تحليلًا فاشلًا إلى حالة تسمح بمحاولة جديدة مع تصفير بيانات النتيجة المؤقتة.

        يحافظ هذا الانتقال على ارتباط التحليل بالتقرير ويمنع استخدام نتيجة فاشلة
        قديمة كأنها تحليل مكتمل.
        """
        with self._session_factory() as session:
            model = session.get(
                ReportAnalysisModel,
                analysis_id,
            )

            if model is None:
                raise ValueError(
                    f"Analysis {analysis_id} not found."
                )

            model.status = (
                AnalysisJobStatus.PENDING.value
            )

            model.health_status = None
            model.summary = None
            model.issues = []
            model.positive_findings = []
            model.recommended_actions = []
            model.analysis_error = None
            model.started_at = None
            model.finished_at = None
            model.duration_ms = None
            model.updated_at = utc_now()

            session.commit()
