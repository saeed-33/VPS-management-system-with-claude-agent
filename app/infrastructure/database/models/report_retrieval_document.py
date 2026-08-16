"""
نموذج الفهرس الذي يربط تقريرًا قابلًا للاسترجاع بنصه وتمثيله الدلالي.
"""
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    Computed,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class ReportRetrievalDocumentModel(Base):
    """
    نسخة مفهرسة من تقرير المراقبة تستخدم للعثور على حالات مشابهة.
    """
    __tablename__ = "report_retrieval_documents"
    __table_args__ = (
        UniqueConstraint("analysis_id", name="uq_report_retrieval_documents_analysis_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(
        ForeignKey("monitoring_reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("report_analyses.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    server_id: Mapped[int] = mapped_column(
        ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    monitoring_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("monitoring_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    command_set_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    connection_successful: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        index=True,
    )
    failed_command_ids: Mapped[list[int]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    error_signatures: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False)
    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('simple', "
            "coalesce(normalized_text, ''))",
            persisted=True,
        ),
        nullable=True,
    )
    structured_features: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    embedding: Mapped[list[float]] = mapped_column(Vector(768), nullable=False)
    embedding_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(150), nullable=False)
    embedding_dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    analysis_health_status: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
