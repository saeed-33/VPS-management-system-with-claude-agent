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
class SpecialistContextSnapshot:
    """
    يحمل الأدلة والحوادث والمعرفة المختارة لسياق اختصاصي واحد.
    """
    task_id: str
    investigation_id: str
    specialist_slug: str
    specialist_name: str
    objective: str
    instructions: str | None
    domains: tuple[str, ...]
    knowledge_query: str
    initial_analysis_summary: str | None
    initial_analysis_issues: tuple[dict, ...]
    evidence: tuple[EvidenceReference, ...]
    incidents: tuple[RetrievedAnalysisContext, ...]
    knowledge_chunks: tuple[KnowledgeRetrievalContext, ...]
    knowledge_sources: tuple[KnowledgeSourceReference, ...]
    rendered_context: str
    character_count: int
