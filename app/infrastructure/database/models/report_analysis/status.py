"""
نموذج تحليل تقرير المراقبة ومحاولاته ونتيجته أو سبب فشله.
"""
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    Float,
    Boolean,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class AnalysisJobStatus(StrEnum):
    """
    حالات تحليل التقرير من الانتظار حتى النجاح أو الفشل.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

