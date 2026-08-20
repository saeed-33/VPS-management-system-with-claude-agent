"""
البحث الدلالي والنصي في مقاطع المعرفة المؤهلة لسياق التحقيق.
"""
from __future__ import annotations

from dataclasses import dataclass

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
