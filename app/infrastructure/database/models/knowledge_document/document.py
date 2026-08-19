"""
نماذج وثائق المعرفة ومقاطعها التي يمكن استرجاعها أثناء التحليل والتحقيق.
"""
from __future__ import annotations
from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class KnowledgeDocumentModel(Base):
    """
    وثيقة معرفة محفوظة بمصدرها ونسختها ونصها وحالتها القابلة للفهرسة.
    """
    __tablename__ = "knowledge_documents"
    __table_args__ = (
        UniqueConstraint("source_id", "canonical_uri", name="uq_knowledge_documents_source_uri"),
        Index("ix_knowledge_documents_source_status", "source_id", "status"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    canonical_uri: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    parser_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    character_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    parsed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
    chunks: Mapped[list["KnowledgeChunkModel"]] = relationship(
        back_populates="document", cascade="all, delete-orphan",
        order_by="KnowledgeChunkModel.chunk_index", lazy="selectin"
    )

