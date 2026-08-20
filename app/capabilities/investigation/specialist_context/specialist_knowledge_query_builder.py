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

class SpecialistKnowledgeQueryBuilder:
    """
    يبني استعلام المعرفة من اختصاصي وإشارات التحقيق.
    """
    def build(
        self,
        *,
        task: SpecialistTask,
        specialist: SpecialistRuntimeDefinition,
        domains: tuple[str, ...],
        initial_analysis_summary: str | None,
        initial_analysis_issues: tuple[dict, ...],
        evidence: tuple[EvidenceReference, ...],
    ) -> str:
        """
        يختار الأدلة والحوادث والمعرفة ويبني النص النهائي لسياق الاختصاصي.
        """
        parts: list[str] = [
            f"Specialist: {specialist.name}",
            f"Objective: {task.objective}",
        ]

        if domains:
            parts.append(
                "Domains: "
                + ", ".join(domains)
            )

        if specialist.knowledge_topics:
            parts.append(
                "Knowledge topics: "
                + ", ".join(
                    specialist.knowledge_topics
                )
            )

        if initial_analysis_summary:
            parts.append(
                "Initial analysis: "
                + initial_analysis_summary
            )

        for issue in initial_analysis_issues[:5]:
            title = str(
                issue.get("title")
                or ""
            ).strip()

            description = str(
                issue.get("description")
                or ""
            ).strip()

            if title or description:
                parts.append(
                    "Issue: "
                    + " — ".join(
                        value
                        for value in (
                            title,
                            description,
                        )
                        if value
                    )
                )

        for item in evidence[:3]:
            excerpt = (
                item.excerpt
                or ""
            ).strip()

            if excerpt:
                parts.append(
                    f"Evidence {item.title}: "
                    f"{excerpt[:800]}"
                )

        return "\n".join(parts)[:8_000]
