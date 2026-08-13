from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class SpecialistDefinitionModel(Base):
    __tablename__ = "specialist_definitions"
    __table_args__ = (
        CheckConstraint("max_rounds >= 1", name="ck_specialist_definitions_max_rounds"),
        CheckConstraint("max_actions >= 0", name="ck_specialist_definitions_max_actions"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    domains: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    trigger_hints: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    knowledge_topics: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    allowed_tool_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100, index=True)
    max_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    max_actions: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    specialist_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
