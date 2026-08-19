"""مسودة مقطع معرفة قبل التخزين."""
from __future__ import annotations
from dataclasses import dataclass, field

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
