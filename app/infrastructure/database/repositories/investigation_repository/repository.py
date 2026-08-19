"""
حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.investigation.investigation import InvestigationModel
from app.infrastructure.database.models.investigation.candidate import InvestigationSpecialistCandidateModel
from app.infrastructure.database.models.server.server import ServerModel
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.investigation.investigation_status import InvestigationStatus
from app.core.contracts.investigations.persist_investigation_dto import PersistInvestigationDTO

from .operations_1 import _InvestigationRepositoryMixin1
from .operations_2 import _InvestigationRepositoryMixin2


class InvestigationRepository(_InvestigationRepositoryMixin1, _InvestigationRepositoryMixin2):
    """
    مسؤول عن حفظ حالة التحقيق ومنع تكرار تشغيل المتخصص وتثبيت نتائجه.
    """

    def __init__(self, session_factory: sessionmaker = SessionLocal) -> None:
        """
        يهيئ مستودع حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
        """
        self._session_factory = session_factory
