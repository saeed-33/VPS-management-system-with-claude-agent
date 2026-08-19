"""سياق مقطع معرفة مسترجع."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class KnowledgeRetrievalContext:
    """
    يمثل مقطع معرفة مسترجعًا مع بيانات المصدر والدرجات والمراتب والتطابقات.
    """
    chunk_id: int
    document_id: int
    source_id: int
    source_slug: str
    source_name: str
    source_uri: str | None
    document_title: str | None
    canonical_uri: str
    section_title: str | None
    page_number: int | None
    content: str
    rank: int
    retrieval_strategy: str
    fusion_score: float
    vector_score: float | None
    full_text_score: float | None
    vector_rank: int | None
    full_text_rank: int | None
    matched_specialist: bool
    matched_domains: tuple[str, ...]
    source_priority: int
