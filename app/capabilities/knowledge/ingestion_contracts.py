"""
نماذج وحالات دورة إدخال وثائق المعرفة.

تصف الحالة مراحل الوثيقة من الانتظار حتى الفهرسة أو الفشل، وتتحقق نماذج
المستند والمقطع من القيم الأساسية قبل تمريرها إلى الخدمات والمستودعات.
"""
from __future__ import annotations
from dataclasses import dataclass, field
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

@dataclass(slots=True, frozen=True)
class ParsedKnowledgeDocument:
    """
    يحمل النص المحلل للوثيقة وURI ونوع الوسيط والعنوان والصفحات والبيانات الوصفية.
    """
    canonical_uri: str
    title: str | None
    media_type: str | None
    text: str
    page_count: int | None = None
    parser_name: str | None = None
    parser_version: str | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        يتحقق من URI والنص وعدد الصفحات في وثيقة المعرفة المنشأة.
        """
        if not self.canonical_uri.strip():
            raise ValueError("canonical_uri must not be empty.")
        if not self.text.strip():
            raise ValueError("Parsed document text must not be empty.")
        if self.page_count is not None and self.page_count < 1:
            raise ValueError("page_count must be >= 1 when provided.")

@dataclass(slots=True, frozen=True)
class KnowledgeChunkDraft:
    """
    يمثل مسودة مقطع قبل تخزينه مع موضعه ومحتواه وعنوانه وحجمه وبياناته.
    """
    chunk_index: int
    content: str
    section_title: str | None = None
    page_number: int | None = None
    token_count: int | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        يتحقق من موضع المقطع ومحتواه ورقم الصفحة وعدد الرموز عند توفرها.
        """
        if self.chunk_index < 0:
            raise ValueError("chunk_index must be >= 0.")
        if not self.content.strip():
            raise ValueError("chunk content must not be empty.")
        if self.page_number is not None and self.page_number < 1:
            raise ValueError("page_number must be >= 1 when provided.")
        if self.token_count is not None and self.token_count < 1:
            raise ValueError("token_count must be >= 1 when provided.")
