"""محتوى مصدر معرفة محمل."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class LoadedKnowledgeContent:
    """
    يحمل البايتات المقروءة من المصدر مع URI القانوني ونوع الوسيط وتلميح العنوان.
    """
    content: bytes
    canonical_uri: str
    media_type: str | None
    title_hint: str | None = None
