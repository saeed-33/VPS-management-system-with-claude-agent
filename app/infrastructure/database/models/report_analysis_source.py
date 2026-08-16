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
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class ReportAnalysisSourceModel(Base):
    """
    يمثل ReportAnalysisSourceModel مسؤولية محددة داخل طبقة Persistence model.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه repositories وطبقة database
    ويعتمد على Base وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    __tablename__ = "report_analysis_sources"
    __table_args__ = (
        UniqueConstraint(
            "analysis_id",
            "source_type",
            "source_report_id",
            "source_analysis_id",
            name="uq_report_analysis_source_identity",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey(
            "report_analyses.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    source_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        index=True,
    )
    source_report_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "monitoring_reports.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    source_analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "report_analyses.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    retrieval_strategy: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )
    similarity_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    rank: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )
    excerpt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    source_metadata: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    used_in_prompt: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
