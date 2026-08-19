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

from .operations_1 import _AnalysisRepositoryMixin1
from .operations_2 import _AnalysisRepositoryMixin2


class AnalysisRepository(_AnalysisRepositoryMixin1, _AnalysisRepositoryMixin2):
    """
    مسؤول عن حالة تحليل التقرير ومحاولاته ونتائج التحليل القابلة لإعادة الاستخدام.
    """

    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        """
        يهيئ مستودع تحليل تقارير المراقبة ومحاولاته ونتائج إعادة الاستخدام والأداء بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
        """
        self._session_factory = session_factory
