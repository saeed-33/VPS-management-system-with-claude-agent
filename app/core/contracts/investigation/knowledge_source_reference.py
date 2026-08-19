"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

from .knowledge_source_type import KnowledgeSourceType

@dataclass(slots=True, frozen=True)
class KnowledgeSourceReference:
    """
    وصف لمصدر معرفة يمكن استخدامه لتفسير دليل أو مقارنة حالة سابقة.
    """
    source_id: str
    source_type: KnowledgeSourceType
    title: str
    url: str | None = None
    topic: str | None = None
    product: str | None = None
    version: str | None = None
    trust_level: str | None = None
    excerpt: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """يتحقق من وجود معرف وعنوان للمصدر قبل ربطه باستنتاج."""
        if not self.source_id.strip():
            raise ValueError(
                "source_id must not be empty."
            )
        if not self.title.strip():
            raise ValueError(
                "Knowledge source title must not be empty."
            )
