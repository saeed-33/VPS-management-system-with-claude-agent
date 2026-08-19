"""Class extracted from specialist_context during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

import json

from app.capabilities.analysis.retrieval.rag_context import (
    RetrievedAnalysisContext,
)

from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.knowledge_source_reference import KnowledgeSourceReference
from app.core.contracts.investigation.knowledge_source_type import KnowledgeSourceType
from app.core.contracts.investigation.specialist_task import SpecialistTask

from app.capabilities.knowledge.retrieval.retriever import KnowledgeHybridRetriever
from app.capabilities.knowledge.retrieval.context import KnowledgeRetrievalContext

from app.capabilities.investigation.specialist_registry.specialist_runtime_definition import SpecialistRuntimeDefinition

@dataclass(slots=True, frozen=True)
class SpecialistContextBudget:
    """
    يضبط حدود النص وعدد الأدلة والحوادث والمعرفة في سياق الاختصاصي.
    """
    max_evidence_items: int = 8
    max_evidence_chars: int = 4_000
    max_incident_contexts: int = 3
    max_incident_chars: int = 4_500
    max_knowledge_chunks: int = 6
    max_knowledge_chars: int = 7_000
    max_total_chars: int = 18_000

    def __post_init__(self) -> None:
        """
        يتحقق من صحة بيانات SpecialistContextBudget قبل استخدامها في التحقيق.
        """
        for field_name in (
            "max_evidence_items",
            "max_evidence_chars",
            "max_incident_contexts",
            "max_incident_chars",
            "max_knowledge_chunks",
            "max_knowledge_chars",
            "max_total_chars",
        ):
            value = getattr(self, field_name)

            if value < 1:
                raise ValueError(
                    f"{field_name} must be >= 1."
                )
