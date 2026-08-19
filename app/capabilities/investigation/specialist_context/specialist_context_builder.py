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

from .context_selector import SpecialistContextSelector
from .context_renderer import SpecialistContextRenderer

class SpecialistContextBuilder:
    """
    ينشئ سياق الاختصاصي المحدود والمنظم من مصادر التحقيق والمعرفة.
    """
    def __init__(
        self,
        *,
        knowledge_retriever: KnowledgeHybridRetriever,
        query_builder: SpecialistKnowledgeQueryBuilder | None = None,
        budget: SpecialistContextBudget | None = None,
    ) -> None:
        """
        يهيئ SpecialistContextBuilder ويربط الاعتماديات اللازمة لدورة التحقيق.
        """
        self._knowledge_retriever = (
            knowledge_retriever
        )
        self._query_builder = (
            query_builder
            or SpecialistKnowledgeQueryBuilder()
        )
        self._budget = (
            budget
            or SpecialistContextBudget()
        )
        self._selector = SpecialistContextSelector(self._budget)
        self._renderer.renderer = SpecialistContextRenderer()

    async def build(
        self,
        *,
        task: SpecialistTask,
        specialist: SpecialistRuntimeDefinition,
        detected_domains: tuple[str, ...] = (),
        evidence: tuple[EvidenceReference, ...] = (),
        initial_analysis_summary: str | None = None,
        initial_analysis_issues: tuple[dict, ...] = (),
        incident_contexts: tuple[
            RetrievedAnalysisContext,
            ...
        ] = (),
    ) -> SpecialistContextSnapshot:
        """
        يختار الأدلة والحوادث والمعرفة ويبني النص النهائي لسياق الاختصاصي.
        """
        if (
            task.specialist_id.strip().casefold()
            != specialist.slug
        ):
            raise ValueError(
                "Task specialist does not match "
                "Specialist definition."
            )

        domains = self._effective_domains(
            specialist=specialist,
            detected_domains=detected_domains,
        )

        selected_evidence = (
            self._selector._select_evidence(
                task=task,
                evidence=evidence,
            )
        )

        query = self._query_builder.build(
            task=task,
            specialist=specialist,
            domains=domains,
            initial_analysis_summary=(
                initial_analysis_summary
            ),
            initial_analysis_issues=(
                initial_analysis_issues
            ),
            evidence=selected_evidence,
        )

        knowledge = tuple(
            await self._knowledge_retriever.retrieve(
                query=query,
                specialist_slug=(
                    specialist.slug
                ),
                domains=domains,
            )
        )

        selected_incidents = (
            self._selector._select_incidents(
                incident_contexts
            )
        )

        selected_knowledge = (
            self._selector._select_knowledge(
                knowledge
            )
        )

        knowledge_sources = (
            self._selector._knowledge_references(
                selected_knowledge
            )
        )

        rendered = self._renderer.render(
            task=task,
            specialist=specialist,
            domains=domains,
            initial_analysis_summary=(
                initial_analysis_summary
            ),
            initial_analysis_issues=(
                initial_analysis_issues
            ),
            evidence=selected_evidence,
            incidents=selected_incidents,
            knowledge=selected_knowledge,
        )

        if (
            len(rendered)
            > self._budget.max_total_chars
        ):
            rendered = rendered[
                : self._budget.max_total_chars
            ].rstrip()

        return SpecialistContextSnapshot(
            task_id=task.task_id,
            investigation_id=(
                task.investigation_id
            ),
            specialist_slug=(
                specialist.slug
            ),
            specialist_name=(
                specialist.name
            ),
            objective=task.objective,
            instructions=(
                specialist.instructions
            ),
            domains=domains,
            knowledge_query=query,
            initial_analysis_summary=(
                initial_analysis_summary
            ),
            initial_analysis_issues=(
                initial_analysis_issues
            ),
            evidence=selected_evidence,
            incidents=selected_incidents,
            knowledge_chunks=(
                selected_knowledge
            ),
            knowledge_sources=(
                knowledge_sources
            ),
            rendered_context=rendered,
            character_count=len(rendered),
        )

    @staticmethod
    def _effective_domains(
        *,
        specialist: SpecialistRuntimeDefinition,
        detected_domains: tuple[str, ...],
    ) -> tuple[str, ...]:
        """
        يحدد المجالات الفعالة من تعريف الاختصاصي وسياق التحقيق.
        """
        detected = tuple(
            dict.fromkeys(
                value.strip().casefold()
                for value in detected_domains
                if value.strip()
            )
        )

        if not detected:
            return specialist.domains

        overlap = tuple(
            domain
            for domain in detected
            if domain
            in specialist.domains
        )

        return overlap or detected
