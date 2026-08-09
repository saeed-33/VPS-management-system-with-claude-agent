from __future__ import annotations

from dataclasses import dataclass

from app.agent.investigation.contracts import (
    InvestigationFinding,
    InvestigationHypothesis,
    SpecialistResult,
    SpecialistTaskStatus,
)
from app.agent.investigation.specialist_context import (
    SpecialistContextSnapshot,
)
from app.agent.investigation.specialist_reasoning_client import (
    SpecialistReasoningClient,
)
from app.shared.dto.specialist_reasoning import (
    SpecialistReasoningOutput,
)


SYSTEM_PROMPT = """You are a read-only infrastructure diagnostic specialist.

Reason only from the supplied Specialist Context.
Do not claim that you executed commands, changed configuration, restarted
services, installed packages, or performed any external action.

Every finding that depends on current evidence must cite only evidence IDs
present in the context. Every finding that depends on technical knowledge
must cite only knowledge source IDs present in the context.

Treat retrieved technical documentation as reference material, not proof that
a condition exists on the monitored server.

If the available information is insufficient, lower confidence and list the
specific missing evidence required to confirm or reject the hypothesis.

recommended_next_specialists may suggest enabled specialist slugs, but this
response does not create or execute any additional specialist.
"""


@dataclass(slots=True, frozen=True)
class SpecialistReasoningExecution:
    result: SpecialistResult
    provider: str
    model: str


class SpecialistReasoningAgent:
    def __init__(
        self,
        *,
        client: SpecialistReasoningClient,
    ) -> None:
        self._client = client

    async def reason(
        self,
        *,
        context: SpecialistContextSnapshot,
        allowed_specialist_slugs: tuple[str, ...] = (),
    ) -> SpecialistReasoningExecution:
        output = await self._client.reason(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=context.rendered_context,
        )

        self._validate_references(
            output=output,
            context=context,
            allowed_specialist_slugs=allowed_specialist_slugs,
        )

        normalized_specialists, dropped_specialists = (
            self._normalize_specialist_recommendations(
                recommendations=tuple(
                    output.recommended_next_specialists
                ),
                allowed_specialist_slugs=(
                    allowed_specialist_slugs
                ),
            )
            if allowed_specialist_slugs
            else (
                tuple(output.recommended_next_specialists),
                (),
            )
        )

        output.recommended_next_specialists = list(
            normalized_specialists
        )

        result = self._to_result(
            output=output,
            context=context,
            dropped_specialist_recommendations=(
                dropped_specialists
            ),
        )

        return SpecialistReasoningExecution(
            result=result,
            provider=self._client.provider_name,
            model=self._client.model_name,
        )

    @staticmethod
    def _validate_references(
        *,
        output: SpecialistReasoningOutput,
        context: SpecialistContextSnapshot,
        allowed_specialist_slugs: tuple[str, ...],
    ) -> None:
        evidence_ids = {
            item.evidence_id
            for item in context.evidence
        }
        knowledge_ids = {
            item.source_id
            for item in context.knowledge_sources
        }

        for finding in output.findings:
            unknown_evidence = (
                set(finding.evidence_ids)
                - evidence_ids
            )
            unknown_knowledge = (
                set(finding.knowledge_source_ids)
                - knowledge_ids
            )

            if unknown_evidence:
                raise ValueError(
                    "Specialist reasoning referenced unknown evidence IDs: "
                    + ", ".join(sorted(unknown_evidence))
                )

            if unknown_knowledge:
                raise ValueError(
                    "Specialist reasoning referenced unknown knowledge IDs: "
                    + ", ".join(sorted(unknown_knowledge))
                )

        for hypothesis in output.hypotheses:
            unknown = (
                set(hypothesis.supporting_evidence_ids)
                | set(hypothesis.contradicting_evidence_ids)
            ) - evidence_ids

            if unknown:
                raise ValueError(
                    "Specialist hypothesis referenced unknown evidence IDs: "
                    + ", ".join(sorted(unknown))
                )


    @staticmethod
    def _normalize_specialist_recommendations(
        *,
        recommendations: tuple[str, ...],
        allowed_specialist_slugs: tuple[str, ...],
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        allowed = {
            value.strip().casefold()
            for value in allowed_specialist_slugs
            if value.strip()
        }

        aliases = {
            "systemd": "systemd-service",
            "service": "systemd-service",
            "services": "systemd-service",
            "network": "linux-network",
            "networking": "linux-network",
            "cpu": "linux-cpu",
            "processor": "linux-cpu",
            "memory": "linux-memory",
            "ram": "linux-memory",
            "storage": "linux-storage",
            "disk": "linux-storage",
            "filesystem": "linux-storage",
            "process": "linux-process",
            "processes": "linux-process",
            "postgres": "postgresql",
            "postgresql": "postgresql",
            "nginx": "nginx",
            "docker": "docker",
        }

        accepted: list[str] = []
        dropped: list[str] = []

        for raw in recommendations:
            value = raw.strip().casefold()
            if not value:
                continue

            candidate = aliases.get(value, value)

            if candidate in allowed:
                if candidate not in accepted:
                    accepted.append(candidate)
            else:
                dropped.append(value)

        return (
            tuple(accepted),
            tuple(dict.fromkeys(dropped)),
        )

    @staticmethod
    def _to_result(
        *,
        output: SpecialistReasoningOutput,
        context: SpecialistContextSnapshot,
        dropped_specialist_recommendations: tuple[str, ...] = (),
    ) -> SpecialistResult:
        findings = tuple(
            InvestigationFinding(
                finding_id=(
                    f"{context.task_id}:finding:{index}"
                ),
                title=item.title,
                description=item.description,
                confidence=item.confidence,
                evidence_ids=tuple(item.evidence_ids),
                knowledge_source_ids=tuple(
                    item.knowledge_source_ids
                ),
            )
            for index, item in enumerate(
                output.findings,
                start=1,
            )
        )

        hypotheses = tuple(
            InvestigationHypothesis(
                hypothesis_id=(
                    f"{context.task_id}:hypothesis:{index}"
                ),
                statement=item.statement,
                confidence=item.confidence,
                supporting_evidence_ids=tuple(
                    item.supporting_evidence_ids
                ),
                contradicting_evidence_ids=tuple(
                    item.contradicting_evidence_ids
                ),
            )
            for index, item in enumerate(
                output.hypotheses,
                start=1,
            )
        )

        used_evidence = tuple(
            dict.fromkeys(
                evidence_id
                for finding in findings
                for evidence_id in finding.evidence_ids
            )
        )
        used_knowledge = tuple(
            dict.fromkeys(
                source_id
                for finding in findings
                for source_id in finding.knowledge_source_ids
            )
        )

        return SpecialistResult(
            task_id=context.task_id,
            specialist_id=context.specialist_slug,
            status=SpecialistTaskStatus.COMPLETED,
            summary=output.summary,
            confidence=output.confidence,
            findings=findings,
            hypotheses=hypotheses,
            ruled_out=tuple(output.ruled_out),
            evidence_ids=used_evidence,
            knowledge_source_ids=used_knowledge,
            missing_evidence=tuple(output.missing_evidence),
            recommended_next_specialists=tuple(
                output.recommended_next_specialists
            ),
            metadata={
                "reasoning_only": True,
                "context_characters": context.character_count,
                "dropped_specialist_recommendations": list(
                    dropped_specialist_recommendations
                ),
            },
        )
