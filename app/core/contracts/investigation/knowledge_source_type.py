"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

class KnowledgeSourceType(StrEnum):
    """
    نوع المرجع المعرفي الذي يساند تفسير حالة السيرفر.
    """
    INCIDENT = "incident"
    INTERNAL_DOCUMENT = "internal_document"
    OFFICIAL_DOCUMENTATION = "official_documentation"
    EXTERNAL_REFERENCE = "external_reference"
