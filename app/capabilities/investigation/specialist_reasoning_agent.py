"""
تحويل reasoning الاختصاصي إلى نتيجة تشخيصية منظمة.

يتحقق الوكيل من مراجع الأدلة ومواقع المصادر وتوصيات الاختصاصي، ثم يعيد نتيجة
قابلة للحفظ والتجميع مع عدم اختلاق مراجع.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.core.contracts.investigation import (
    InvestigationFinding,
    InvestigationHypothesis,
    SpecialistResult,
    SpecialistTaskStatus,
)
from app.core.policies.diagnostic_tools import (
    DiagnosticToolCall,
)
from app.capabilities.investigation.specialist_context import (
    SpecialistContextSnapshot,
)
from app.capabilities.investigation.specialist_reasoning_client import (
    SpecialistReasoningClient,
)
from app.core.contracts.specialist_reasoning import (
    SpecialistReasoningOutput,
)
from app.capabilities.investigation.source_location import extract_source_locations


SYSTEM_PROMPT = """You are a read-only infrastructure diagnostic specialist.

Reason only from the supplied Specialist Context.
Do not claim that you executed commands, changed configuration, restarted
services, installed packages, or performed any external action.

Every finding that depends on current evidence must cite only evidence IDs
present in the context. Every finding that depends on technical knowledge
must cite only knowledge source IDs present in the context.

Current Evidence blocks contain an explicit `evidence_id:` field. Only the
exact value after `evidence_id:` is a valid Evidence ID. Do not prepend
`evidence:` or any other namespace to it. Error messages, hostnames, command
output, Initial Analysis text, and Initial Issues text are never Evidence IDs
by themselves. Never copy evidence text into an evidence_ids field.

Technical Knowledge blocks contain an explicit `knowledge_source_id:` field.
Only that exact value is a valid knowledge source ID.

Treat retrieved technical documentation as reference material, not proof that
a condition exists on the monitored server.

The Objective field in the Specialist Context is authoritative. Do not
reinterpret, rename, or replace it with a different problem statement.
Do not write meta commentary such as "the user provided", "the user asks",
"no question was provided", or descriptions of the Tool catalog. Act as the
assigned Specialist and answer the Objective itself.
Every hypothesis, Tool request, finding, and conclusion must be directly
relevant to that Objective or to a concrete sub-hypothesis required to test it.

Prefer the narrowest diagnostic Tool which directly tests the current
hypothesis. Do not request broad CPU, memory, routing, or service inventory
checks merely because those Tools are available unless the Objective or
existing Evidence gives a concrete reason to do so.

If the available information is insufficient, lower confidence and list the
specific missing evidence required to confirm or reject the hypothesis.

When an Available Diagnostic Tools catalog is supplied, you may request live
evidence through diagnostic_tool_requests. Request only tool IDs from that
catalog. Never put shell commands, shell operators, pipelines, redirections,
or executable text in arguments. Use only the typed arguments defined by the
catalog.

Request the minimum evidence needed. Do not request a Tool when the existing
evidence is already sufficient. If no additional diagnostic execution is
needed, diagnostic_tool_requests must be empty.

recommended_next_specialists may suggest enabled specialist slugs, but this
response does not create or execute any additional specialist.
"""


@dataclass(slots=True, frozen=True)
class SpecialistDiagnosticToolRequest:
    """
    يمثل طلب الاختصاصي لتشغيل أداة تشخيصية.
    """
    call: DiagnosticToolCall
    rationale: str


@dataclass(slots=True, frozen=True)
class SpecialistReasoningExecution:
    """
    يمثل استجابة reasoning الاختصاصي مع الادعاءات والتوصيات والمراجع.
    """
    result: SpecialistResult
    provider: str
    model: str
    diagnostic_tool_requests: tuple[
        SpecialistDiagnosticToolRequest,
        ...
    ] = ()


class SpecialistReasoningAgent:
    """
    يتحقق من استجابة الاختصاصي ويحوّلها إلى نتيجة تشخيصية قابلة للحفظ.
    """
    def __init__(
        self,
        *,
        client: SpecialistReasoningClient,
    ) -> None:
        """
        يهيئ SpecialistReasoningAgent ويربط الاعتماديات اللازمة لدورة التحقيق.
        """
        self._client = client

    async def reason(
        self,
        *,
        context: SpecialistContextSnapshot,
        allowed_specialist_slugs: tuple[str, ...] = (),
        diagnostic_tool_catalog: str | None = None,
        force_final_synthesis: bool = False,
    ) -> SpecialistReasoningExecution:
        """
        ينفذ reasoning الاختصاصي ويتحقق من المراجع ويعيد النتيجة المنظمة.
        """
        user_prompt = (
            "## Mandatory Investigation Objective\n"
            + context.objective
            + (
                "\n\nThis Objective is the task to solve. "
                "Do not replace it with a generic incident, "
                "a connectivity problem, or a description of "
                "the available Tools. Your summary and every "
                "diagnostic action must directly advance this "
                "Objective.\n\n"
            )
            + context.rendered_context
        )

        evidence_ids = tuple(
            dict.fromkeys(
                item.evidence_id
                for item in context.evidence
            )
        )
        user_prompt += (
            "\n\n## Evidence ID Allowlist\n"
            "The only valid values for finding.evidence_ids, "
            "hypothesis.supporting_evidence_ids, and "
            "hypothesis.contradicting_evidence_ids are the exact opaque "
            "Evidence IDs listed below. Copy the identifier token only. "
            "Never copy an Evidence title, observation, excerpt, command, "
            "status line, hostname, or any other raw text into an Evidence "
            "ID field. If no listed ID supports a statement, return an empty "
            "list.\n"
            "Allowed Evidence IDs: "
            + (
                ", ".join(
                    f"`{value}`"
                    for value in evidence_ids
                )
                if evidence_ids
                else "(none)"
            )
        )

        if force_final_synthesis:
            user_prompt += (
                "\n\n## Final Synthesis Required\n"
                "No further diagnostic execution is available in this pass. "
                "Do not request any Diagnostic Tool. Produce a short final "
                "diagnostic conclusion using only the current Evidence.\n"
                "\n## Final Synthesis Size Limits\n"
                "- summary: at most 350 characters.\n"
                "- findings: at most 2.\n"
                "- each finding description: at most 240 characters.\n"
                "- hypotheses: at most 1.\n"
                "- ruled_out: at most 2.\n"
                "- missing_evidence: at most 3 short items.\n"
                "- recommended_next_specialists: at most 1 enabled slug, "
                "and only when another Specialist domain is genuinely "
                "required.\n"
                "- diagnostic_tool_requests: always empty.\n"
                "\n## Provenance Rules For Final Synthesis\n"
                "Evidence IDs and Knowledge Source IDs are opaque identifiers. "
                "Copy them exactly from explicit `evidence_id:` or "
                "`knowledge_source_id:` fields in the context. Never derive "
                "an ID from a module name, command name, hostname, prose, or "
                "documentation content. If no exact Knowledge Source ID is "
                "needed, use an empty knowledge_source_ids list. Do not copy "
                "or paraphrase long command output into the response."
            )

        if diagnostic_tool_catalog and not force_final_synthesis:
            user_prompt += (
                "\n\n## Available Diagnostic Tools\n"
                + diagnostic_tool_catalog
                + (
                    "\n\n## Objective Reminder\n"
                    + context.objective
                    + (
                        "\nSelect only the minimum directly relevant "
                        "Tool evidence needed to answer this Objective. "
                        "The Tool catalog is capability metadata, not the "
                        "problem statement."
                    )
                )
            )

        output = await self._client.reason(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
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

        diagnostic_requests = tuple(
            SpecialistDiagnosticToolRequest(
                call=DiagnosticToolCall(
                    tool_id=item.tool_id,
                    arguments=dict(
                        item.arguments
                    ),
                ),
                rationale=item.rationale,
            )
            for item
            in output.diagnostic_tool_requests
        )

        if force_final_synthesis:
            diagnostic_requests = ()

        return SpecialistReasoningExecution(
            result=result,
            provider=self._client.provider_name,
            model=self._client.model_name,
            diagnostic_tool_requests=(
                diagnostic_requests
            ),
        )

    @staticmethod
    def _validate_references(
        *,
        output: SpecialistReasoningOutput,
        context: SpecialistContextSnapshot,
        allowed_specialist_slugs: tuple[str, ...],
    ) -> None:
        """
        يتحقق من أن مراجع النتيجة تشير إلى أدلة أو مواقع موجودة.
        """
        evidence_ids = {
            item.evidence_id
            for item in context.evidence
        }
        knowledge_ids = {
            item.source_id
            for item in context.knowledge_sources
        }

        def normalize_reference(
            value: str,
            *,
            namespace: str,
            allowed: set[str],
        ) -> str:
            """
            يطبع مرجعًا ويزيل بادئته مع التأكد من بقائه ضمن الأدلة المسموحة.
            """
            candidate = value.strip()

            prefix = namespace + ":"

            if candidate.startswith(prefix):
                suffix = candidate[len(prefix):]

                # لا نقبل تطبيع المعرف إلا إذا ظل يشير إلى دليل حقيقي موجود
                # في سياق التحقيق المقدم.
                if suffix in allowed:
                    return suffix

            return candidate

        for finding in output.findings:
            finding.evidence_ids = [
                normalize_reference(
                    value,
                    namespace="evidence",
                    allowed=evidence_ids,
                )
                for value in finding.evidence_ids
            ]

            finding.knowledge_source_ids = [
                normalize_reference(
                    value,
                    namespace="knowledge",
                    allowed=knowledge_ids,
                )
                for value in finding.knowledge_source_ids
            ]
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
            hypothesis.supporting_evidence_ids = [
                normalize_reference(
                    value,
                    namespace="evidence",
                    allowed=evidence_ids,
                )
                for value in hypothesis.supporting_evidence_ids
            ]

            hypothesis.contradicting_evidence_ids = [
                normalize_reference(
                    value,
                    namespace="evidence",
                    allowed=evidence_ids,
                )
                for value in hypothesis.contradicting_evidence_ids
            ]

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
        """
        يطبع توصيات الاختصاصي إلى شكل آمن موحد.
        """
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
        """
        يحوّل استجابة النموذج إلى عقد تنفيذ اختصاصي.
        """
        evidence_by_id = {
            item.evidence_id: item
            for item in context.evidence
        }

        def finding_metadata(evidence_ids: tuple[str, ...]) -> dict:
            """
            يجمع البيانات الوصفية لمواقع الأدلة التي استند إليها الاكتشاف.
            """
            locations = []
            for evidence_id in evidence_ids:
                evidence = evidence_by_id.get(evidence_id)
                if evidence is None:
                    continue
                raw_locations = evidence.metadata.get("code_locations", [])
                if raw_locations:
                    for raw_location in raw_locations:
                        location = dict(raw_location)
                        location["evidence_ids"] = [evidence_id]
                        locations.append(location)
                elif evidence.excerpt:
                    locations.extend(
                        item.to_dict()
                        for item in extract_source_locations(
                            evidence.excerpt,
                            evidence_ids=(evidence_id,),
                        )
                    )
            unique = []
            seen = set()
            for location in locations:
                key = (
                    location.get("file_path"),
                    location.get("line_number"),
                    location.get("column_number"),
                    tuple(location.get("evidence_ids", [])),
                )
                if key not in seen:
                    seen.add(key)
                    unique.append(dict(location))
            return {"code_locations": unique} if unique else {}

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
                metadata=finding_metadata(tuple(item.evidence_ids)),
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
                "diagnostic_tool_request_count": len(
                    output.diagnostic_tool_requests
                ),
                "dropped_specialist_recommendations": list(
                    dropped_specialist_recommendations
                ),
            },
        )
