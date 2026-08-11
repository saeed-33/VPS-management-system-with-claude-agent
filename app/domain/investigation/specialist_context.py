from __future__ import annotations

from dataclasses import dataclass
import json

from app.domain.analysis.retrieval.rag_context import (
    RetrievedAnalysisContext,
)
from app.domain.investigation.contracts import (
    EvidenceReference,
    KnowledgeSourceReference,
    KnowledgeSourceType,
    SpecialistTask,
)
from app.domain.knowledge.retrieval import (
    KnowledgeHybridRetriever,
    KnowledgeRetrievalContext,
)
from app.domain.investigation.specialist_registry import (
    SpecialistRuntimeDefinition,
)


@dataclass(slots=True, frozen=True)
class SpecialistContextBudget:
    max_evidence_items: int = 8
    max_evidence_chars: int = 4_000
    max_incident_contexts: int = 3
    max_incident_chars: int = 4_500
    max_knowledge_chunks: int = 6
    max_knowledge_chars: int = 7_000
    max_total_chars: int = 18_000

    def __post_init__(self) -> None:
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


@dataclass(slots=True, frozen=True)
class SpecialistContextSnapshot:
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


class SpecialistKnowledgeQueryBuilder:
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


class SpecialistContextBuilder:
    def __init__(
        self,
        *,
        knowledge_retriever: KnowledgeHybridRetriever,
        query_builder: SpecialistKnowledgeQueryBuilder | None = None,
        budget: SpecialistContextBudget | None = None,
    ) -> None:
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
            self._select_evidence(
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
            self._select_incidents(
                incident_contexts
            )
        )

        selected_knowledge = (
            self._select_knowledge(
                knowledge
            )
        )

        knowledge_sources = (
            self._knowledge_references(
                selected_knowledge
            )
        )

        rendered = self._render(
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

    def _select_evidence(
        self,
        *,
        task: SpecialistTask,
        evidence: tuple[EvidenceReference, ...],
    ) -> tuple[EvidenceReference, ...]:
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

    @staticmethod
    def _render(
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
