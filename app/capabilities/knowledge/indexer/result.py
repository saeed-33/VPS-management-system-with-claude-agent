"""نتيجة فهرسة وثيقة معرفة."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class KnowledgeIndexingResult:
    """
    يلخص نتيجة فهرسة وثيقة وعدد المقاطع المحدثة والمتخطاة ومعلومات embedding.
    """
    document_id: int
    total_chunks: int
    indexed_chunks: int
    skipped_chunks: int
    provider: str
    model: str
    dimensions: int
    status: str
