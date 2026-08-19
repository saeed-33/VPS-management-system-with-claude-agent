"""
نموذج هوية السيرفر وإعدادات الاتصال وحالة آخر مراقبة.
"""
from datetime import datetime
from enum import StrEnum
from sqlalchemy import ForeignKey
from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class ServerStatus(StrEnum):
    """
    الحالات التشغيلية التي تصف اتصال السيرفر وآخر نتيجة مراقبة له.
    """
    UNKNOWN = "unknown"
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"

