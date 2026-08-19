"""حالات دورة إدخال وثائق المعرفة."""
from __future__ import annotations
from enum import StrEnum

class KnowledgeDocumentStatus(StrEnum):
    """
    يمثل الحالات المتتابعة لوثيقة المعرفة أثناء الإدخال والمعالجة والفهرسة.
    """
    PENDING = "pending"
    FETCHED = "fetched"
    PARSED = "parsed"
    CHUNKED = "chunked"
    INDEXED = "indexed"
    FAILED = "failed"
