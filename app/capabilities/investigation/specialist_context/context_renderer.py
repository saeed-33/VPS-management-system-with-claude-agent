"""Class extracted from specialist_context during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

import json

from app.core.contracts.analysis.retrieved_analysis_context import (
    RetrievedAnalysisContext,
)

from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.knowledge_source_reference import KnowledgeSourceReference
from app.core.contracts.investigation.knowledge_source_type import KnowledgeSourceType
from app.core.contracts.investigation.specialist_task import SpecialistTask

from app.core.contracts.knowledge_sources.knowledge_retrieval_context import KnowledgeRetrievalContext

from app.capabilities.investigation.specialist_registry.specialist_runtime_definition import SpecialistRuntimeDefinition

from .specialist_context_budget import SpecialistContextBudget

from .specialist_context_snapshot import SpecialistContextSnapshot

from .specialist_knowledge_query_builder import SpecialistKnowledgeQueryBuilder

class SpecialistContextRenderer:
    """ينسق مكونات سياق الاختصاصي في نص قابل للعرض."""

    @staticmethod
    def render(
        *,
        task: SpecialistTask,
        specialist: SpecialistRuntimeDefinition,
        domains: tuple[str, ...],
        initial_analysis_summary: str | None,
        initial_analysis_issues: tuple[dict, ...],
        evidence: tuple[EvidenceReference, ...],
        incidents: tuple[
            RetrievedAnalysisContext,
            ...
        ],
        knowledge: tuple[
            KnowledgeRetrievalContext,
            ...
        ],
    ) -> str:
        """
        ينسق مكونات السياق في نص مطالبة منظم.
        """
        sections: list[str] = []

        sections.append(
            "## Specialist\n"
            f"slug: {specialist.slug}\n"
            f"name: {specialist.name}\n"
            f"objective: {task.objective}\n"
            "domains: "
            + (
                ", ".join(domains)
                or "—"
            )
        )

        if specialist.instructions:
            sections.append(
                "## Specialist Instructions\n"
                + specialist.instructions
            )

        if initial_analysis_summary:
            sections.append(
                "## Initial Analysis\n"
                + initial_analysis_summary
            )

        if initial_analysis_issues:
            issue_lines = [
                "- "
                + json.dumps(
                    item,
                    ensure_ascii=False,
                    sort_keys=True,
                )
                for item
                in initial_analysis_issues
            ]

            sections.append(
                "## Initial Issues\n"
                + "\n".join(
                    issue_lines
                )
            )

        if evidence:
            evidence_parts = []

            for item in evidence:
                evidence_parts.append(
                    "[evidence]\n"
                    f"evidence_id: {item.evidence_id}\n"
                    f"title: {item.title}\n"
                    f"kind: {item.kind.value}\n"
                    f"excerpt: "
                    f"{item.excerpt or '—'}"
                )

            sections.append(
                "## Current Evidence\n"
                + "\n\n".join(
                    evidence_parts
                )
            )

        if incidents:
            incident_parts = []

            for item in incidents:
                incident_parts.append(
                    "[incident:"
                    f"report-{item.source_report_id}"
                    f"/analysis-{item.source_analysis_id}]\n"
                    f"strategy: "
                    f"{item.retrieval_strategy}\n"
                    f"score: {item.score:.5f}\n"
                    f"summary: "
                    f"{item.summary or '—'}\n"
                    "issues: "
                    + json.dumps(
                        item.issues,
                        ensure_ascii=False,
                    )
                )

            sections.append(
                "## Relevant Historical Incidents\n"
                + "\n\n".join(
                    incident_parts
                )
            )

        if knowledge:
            knowledge_parts = []

            for item in knowledge:
                canonical_source_id = (
                    f"knowledge-chunk:{item.chunk_id}"
                )

                citation = (
                    "[knowledge]\n"
                    f"knowledge_source_id: {canonical_source_id}"
                )

                location = []

                if item.section_title:
                    location.append(
                        item.section_title
                    )

                if item.page_number:
                    location.append(
                        f"page {item.page_number}"
                    )

                knowledge_parts.append(
                    f"{citation}\n"
                    f"source: {item.source_slug}\n"
                    f"url: {item.canonical_uri}\n"
                    f"location: "
                    f"{' / '.join(location) or '—'}\n"
                    f"strategy: "
                    f"{item.retrieval_strategy}\n"
                    f"content:\n"
                    f"{item.content}"
                )

            sections.append(
                "## Technical Knowledge\n"
                + "\n\n".join(
                    knowledge_parts
                )
            )

        return "\n\n".join(
            sections
        ).strip()
