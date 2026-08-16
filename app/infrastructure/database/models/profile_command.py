"""
نموذج persistence يطابق entity أو projection مخزنة في PostgreSQL.

الموقع في المعمارية: Persistence model.
يُستدعى بواسطة: repositories وطبقة database.
يعتمد مباشرة على: app.infrastructure.database.base، app.core.utils.datetime.
الحد المعماري: لا يحتوي على orchestration أو اتصال خارجي.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class MonitoringProfileCommandModel(Base):
    """
    يمثل MonitoringProfileCommandModel مسؤولية محددة داخل طبقة Persistence model.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه repositories وطبقة database
    ويعتمد على Base وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    __tablename__ = "monitoring_profile_commands"

    __table_args__ = (
        UniqueConstraint(
            "profile_id",
            "command_id",
            name="uq_monitoring_profile_command",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    profile_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitoring_profiles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    command_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitor_commands.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    execution_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    custom_timeout_seconds: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )