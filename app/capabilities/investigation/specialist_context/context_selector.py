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

from .specialist_context_budget import SpecialistContextBudget

from .specialist_context_snapshot import SpecialistContextSnapshot

from .specialist_knowledge_query_builder import SpecialistKnowledgeQueryBuilder

class SpecialistContextSelector:
    """ينتقي الأدلة والحوادث ومقاطع المعرفة ضمن الميزانية."""

    def __init__(self, budget: SpecialistContextBudget) -> None:
        self._budget = budget

    def _select_evidence(
        self,
        *,
        task: SpecialistTask,
        evidence: tuple[EvidenceReference, ...],
    ) -> tuple[EvidenceReference, ...]:
        """
        ينتقي الأدلة الأعلى صلة ضمن ميزانية السياق.
        """
        if task.evidence_ids:
            allowed = set(
                task.evidence_ids
            )

            evidence = tuple(
                item
                for item in evidence
                if item.evidence_id
                in allowed
            )

        selected: list[
            EvidenceReference
        ] = []

        used_chars = 0

        for item in evidence:
            if (
                len(selected)
                >= self._budget.max_evidence_items
            ):
                break

            cost = len(
                item.excerpt
                or item.title
            )

            if (
                selected
                and used_chars + cost
                > self._budget.max_evidence_chars
            ):
                break

            selected.append(item)
            used_chars += cost

        return tuple(selected)

    def _select_incidents(
        self,
        incidents: tuple[
            RetrievedAnalysisContext,
            ...
        ],
    ) -> tuple[
        RetrievedAnalysisContext,
        ...
    ]:
        """
        ينتقي الحوادث التاريخية التي تساعد الاختصاصي.
        """
        selected = []
        used_chars = 0

        for item in incidents:
            if (
                len(selected)
                >= self._budget.max_incident_contexts
            ):
                break

            cost = len(
                item.summary
                or ""
            )

            cost += sum(
                len(
                    json.dumps(
                        issue,
                        ensure_ascii=False,
                    )
                )
                for issue in item.issues
            )

            if (
                selected
                and used_chars + cost
                > self._budget.max_incident_chars
            ):
                break

            selected.append(item)
            used_chars += cost

        return tuple(selected)

    def _select_knowledge(
        self,
        chunks: tuple[
            KnowledgeRetrievalContext,
            ...
        ],
    ) -> tuple[
        KnowledgeRetrievalContext,
        ...
    ]:
        """
        ينتقي مقاطع المعرفة المطابقة للمجالات والاختصاص.
        """
        selected = []
        used_chars = 0

        for item in chunks:
            if (
                len(selected)
                >= self._budget.max_knowledge_chunks
            ):
                break

            cost = len(item.content)

            if (
                selected
                and used_chars + cost
                > self._budget.max_knowledge_chars
            ):
                break

            selected.append(item)
            used_chars += cost

        return tuple(selected)

    @staticmethod
    def _knowledge_references(
        chunks: tuple[
            KnowledgeRetrievalContext,
            ...
        ],
    ) -> tuple[
        KnowledgeSourceReference,
        ...
    ]:
        """
        ينشئ مراجع مختصرة لمصادر المعرفة المختارة.
        """
        result: list[
            KnowledgeSourceReference
        ] = []

        seen: set[str] = set()

        for item in chunks:
            source_id = (
                f"knowledge-chunk:"
                f"{item.chunk_id}"
            )

            if source_id in seen:
                continue

            seen.add(source_id)

            result.append(
                KnowledgeSourceReference(
                    source_id=source_id,
                    source_type=(
                        KnowledgeSourceType
                        .OFFICIAL_DOCUMENTATION
                    ),
                    title=(
                        item.document_title
                        or item.source_name
                    ),
                    url=(
                        item.canonical_uri
                        or item.source_uri
                    ),
                    topic=(
                        item.section_title
                    ),
                    excerpt=(
                        item.content[:1_200]
                    ),
                    metadata={
                        "chunk_id": (
                            item.chunk_id
                        ),
                        "document_id": (
                            item.document_id
                        ),
                        "source_id": (
                            item.source_id
                        ),
                        "source_slug": (
                            item.source_slug
                        ),
                        "page_number": (
                            item.page_number
                        ),
                        "rank": item.rank,
                        "strategy": (
                            item.retrieval_strategy
                        ),
                        "fusion_score": (
                            item.fusion_score
                        ),
                    },
                )
            )

        return tuple(result)
