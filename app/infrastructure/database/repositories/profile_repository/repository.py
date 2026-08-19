"""
ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها.
"""
from dataclasses import asdict
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.monitor_command import (
    MonitorCommandModel,
)
from app.infrastructure.database.models.monitoring_profile import (
    MonitoringProfileModel,
)
from app.infrastructure.database.models.profile_command import (
    MonitoringProfileCommandModel,
)
from app.infrastructure.database.models.server.server import ServerModel
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.profiles.create_monitoring_profile_dto import CreateMonitoringProfileDTO
from app.core.contracts.profiles.monitoring_profile_command_config import MonitoringProfileCommandConfig
from app.core.contracts.profiles.update_monitoring_profile_dto import UpdateMonitoringProfileDTO
from app.core.utils.datetime import utc_now

from .profile_assignments import _ProfileAssignmentsMixin
from .profile_queries import _ProfileQueriesMixin


class MonitoringProfileRepository(_ProfileQueriesMixin, _ProfileAssignmentsMixin):
    """
    مسؤول عن ملفات المراقبة وعلاقاتها بالفحوص والسيرفرات.
    """

    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        """
        يهيئ مستودع ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
        """
        self._session_factory = session_factory
