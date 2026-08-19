"""
تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها.
"""
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from dataclasses import asdict

from app.infrastructure.database.models.monitor_command import (
    MonitorCommandModel,
)
from app.infrastructure.database.models.profile_command import (
    MonitoringProfileCommandModel,
)
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.commands.command_execution_config import CommandExecutionConfig
from app.core.contracts.commands.create_command_dto import CreateCommandDTO
from app.core.contracts.commands.update_command_dto import UpdateCommandDTO
from app.core.exceptions.command_already_assigned_error import CommandAlreadyAssignedError
from app.core.utils.datetime import utc_now

from .operations_1 import _CommandRepositoryMixin1
from .operations_2 import _CommandRepositoryMixin2


class CommandRepository(_CommandRepositoryMixin1, _CommandRepositoryMixin2):
    """
    مسؤول عن تعريف فحوص المراقبة وربطها بالسيرفرات وقراءتها بترتيب التنفيذ.
    """

    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        """
        يهيئ مستودع تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
        """
        self._session_factory = session_factory
