"""
البحث الدلالي والنصي في مقاطع المعرفة المؤهلة لسياق التحقيق.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import cast, func, or_, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.knowledge_document.chunk import KnowledgeChunkModel
from app.infrastructure.database.models.knowledge_document.document import KnowledgeDocumentModel
from app.infrastructure.database.models.knowledge_source import (
    KnowledgeSourceModel,
)
from app.infrastructure.database.session import SessionLocal


@dataclass(slots=True, frozen=True)


class KnowledgeSearchRow:
    """
    صف نتيجة بحث معرفة يحمل النص والمصدر والدرجات اللازمة لترتيب السياق.
    """
    chunk_id: int
    document_id: int
    source_id: int
    source_slug: str
    source_name: str
    source_uri: str | None
    source_priority: int
    domains: tuple[str, ...]
    specialist_slugs: tuple[str, ...]
    document_title: str | None
    canonical_uri: str
    section_title: str | None
    page_number: int | None
    content: str
    score: float
