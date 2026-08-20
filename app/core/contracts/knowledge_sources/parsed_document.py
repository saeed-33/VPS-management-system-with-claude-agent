"""وثيقة معرفة بعد تحليل محتواها."""
from __future__ import annotations
from dataclasses import dataclass, field

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
