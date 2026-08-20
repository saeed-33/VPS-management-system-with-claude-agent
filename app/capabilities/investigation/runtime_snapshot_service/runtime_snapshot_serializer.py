"""
حفظ ودمج لقطة تشغيل التحقيق.

تدير الخدمة حالة التحقيق المتدرجة، وتدمج نتائج الاختصاصيين والتشخيص النهائي
والأدلة والادعاءات مع الحفاظ على البيانات القابلة للتسلسل.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.capabilities.investigation.correlation.final_diagnosis import FinalDiagnosis
from app.core.contracts.final_diagnosis.final_diagnosis_narrative import FinalDiagnosisNarrative
from app.capabilities.investigation.execution_contracts.investigation_execution_result import InvestigationExecutionResult
from app.core.contracts.investigation.evidence_kind import EvidenceKind
from app.core.contracts.investigation.evidence_reference import EvidenceReference


from .json_safe import JsonSafeValueConverter

class InvestigationRuntimeSnapshotSerializer:
    """تحويل بيانات لقطات التحقيق إلى تمثيل قابل للتسلسل."""

    def __init__(self) -> None:
        self._json_safe_converter = JsonSafeValueConverter()

    def json_safe(self, value: Any) -> Any:
        return self._json_safe_converter.convert(value)


    def _serialize_accepted_run(self, task, loop_result) -> dict:
        """
        يحوّل  accepted run إلى تمثيل قابل للتسلسل.
        """
        result = loop_result.final_result
        return {
            "specialist_slug": task.specialist_id,
            "task_id": task.task_id,
            "task": {
                "server_id": task.server_id,
                "report_id": task.report_id,
                "objective": task.objective,
                "round_number": task.round_number,
                "metadata": dict(task.metadata or {}),
            },
            "status": result.status.value,
            "confidence": result.confidence,
            "summary": result.summary,
            "findings": [self._serialize_finding(item) for item in result.findings],
            "hypotheses": [self._serialize_hypothesis(item) for item in result.hypotheses],
            "ruled_out": list(result.ruled_out),
            "recommended_next_specialists": list(result.recommended_next_specialists),
            "evidence_ids": list(result.evidence_ids),
            "knowledge_source_ids": list(result.knowledge_source_ids),
            "missing_evidence": list(result.missing_evidence),
            "rounds_completed": loop_result.rounds_completed,
            "actions_executed": loop_result.actions_executed,
            "investigation_actions_used": loop_result.investigation_actions_used,
            "stop_reason": loop_result.stop_reason.value,
            "provider": loop_result.provider,
            "model": loop_result.model,
            "metadata": dict(result.metadata or {}),
        }

    def _serialize_finding(self, finding) -> dict:
        """
        يحوّل  finding إلى تمثيل قابل للتسلسل.
        """
        return {
            "finding_id": finding.finding_id,
            "title": finding.title,
            "description": finding.description,
            "confidence": finding.confidence,
            "evidence_ids": list(finding.evidence_ids),
            "knowledge_source_ids": list(finding.knowledge_source_ids),
            "missing_evidence": list(finding.missing_evidence),
            "metadata": dict(finding.metadata or {}),
        }

    def _serialize_hypothesis(self, hypothesis) -> dict:
        """
        يحوّل  hypothesis إلى تمثيل قابل للتسلسل.
        """
        return {
            "hypothesis_id": hypothesis.hypothesis_id,
            "statement": hypothesis.statement,
            "confidence": hypothesis.confidence,
            "supporting_evidence_ids": list(hypothesis.supporting_evidence_ids),
            "contradicting_evidence_ids": list(hypothesis.contradicting_evidence_ids),
            "metadata": dict(hypothesis.metadata or {}),
        }

    def _serialize_run(
        self,
        run,
    ) -> dict:
        """
        يحوّل  run إلى تمثيل قابل للتسلسل.
        """
        loop = run.loop_result

        return {
            "specialist_slug": (
                run.specialist_slug
            ),
            "task_id": run.task.task_id,
            "status": (
                run.result.status.value
            ),
            "confidence": (
                run.result.confidence
            ),
            "summary": run.result.summary,
            "recommended_next_specialists": list(
                run.result
                .recommended_next_specialists
            ),
            "rounds_completed": (
                loop.rounds_completed
                if loop is not None
                else None
            ),
            "actions_executed": (
                loop.actions_executed
                if loop is not None
                else 0
            ),
            "stop_reason": (
                loop.stop_reason.value
                if loop is not None
                else None
            ),
            "evidence_ids": list(
                run.result.evidence_ids
            ),
            "metadata": dict(
                run.result.metadata
                or {}
            ),
        }

    def _serialize_evidence(
        self,
        item,
        *,
        investigation_id: str,
        server_id: int,
        report_id: int,
    ) -> dict:
        """
        يحوّل  evidence إلى تمثيل قابل للتسلسل.
        """
        metadata = dict(item.metadata or {})
        metadata.setdefault(
            "investigation_id",
            investigation_id,
        )
        metadata.setdefault("server_id", server_id)
        metadata.setdefault("report_id", report_id)

        return {
            "evidence_id": item.evidence_id,
            "kind": item.kind.value,
            "title": item.title,
            "source_id": item.source_id,
            "excerpt": item.excerpt,
            "metadata": metadata,
        }

    def _serialize_claim(
        self,
        claim,
    ) -> dict:
        """
        يحوّل  claim إلى تمثيل قابل للتسلسل.
        """
        return {
            "claim_id": claim.claim_id,
            "title": claim.title,
            "description": (
                claim.description
            ),
            "certainty": (
                claim.certainty.value
            ),
            "confidence": (
                claim.confidence
            ),
            "specialist_slugs": list(
                claim.specialist_slugs
            ),
            "evidence_ids": list(
                claim.evidence_ids
            ),
            "knowledge_source_ids": list(
                claim.knowledge_source_ids
            ),
            "missing_evidence": list(
                claim.missing_evidence
            ),
            "metadata": dict(
                claim.metadata
                or {}
            ),
        }

    def _serialize_conflict(
        self,
        conflict,
    ) -> dict:
        """
        يحوّل  conflict إلى تمثيل قابل للتسلسل.
        """
        return {
            "conflict_id": (
                conflict.conflict_id
            ),
            "title": conflict.title,
            "diagnostic_states": list(
                conflict.diagnostic_states
            ),
            "specialist_slugs": list(
                conflict.specialist_slugs
            ),
            "evidence_ids": list(
                conflict.evidence_ids
            ),
            "source_finding_ids": list(
                conflict.source_finding_ids
            ),
            "description": (
                conflict.description
            ),
        }

    def _serialize_final_diagnosis(
        self,
        diagnosis: FinalDiagnosis,
    ) -> dict:
        """
        يحوّل  final diagnosis إلى تمثيل قابل للتسلسل.
        """
        return {
            "investigation_id": (
                diagnosis.investigation_id
            ),
            "summary": diagnosis.summary,
            "confirmed_count": (
                diagnosis.confirmed_count
            ),
            "probable_count": (
                diagnosis.probable_count
            ),
            "unknown_count": (
                diagnosis.unknown_count
            ),
            "conflict_count": (
                diagnosis.conflict_count
            ),
            "evidence_ids": list(
                diagnosis.evidence_ids
            ),
            "specialist_slugs": list(
                diagnosis.specialist_slugs
            ),
            "metadata": dict(
                diagnosis.metadata
                or {}
            ),
        }

    def _serialize_narrative(
        self,
        narrative: FinalDiagnosisNarrative,
    ) -> dict:
        """
        يحوّل  narrative إلى تمثيل قابل للتسلسل.
        """
        return {
            "summary": narrative.summary,
            "claim_ids": list(
                narrative.claim_ids
            ),
            "conflict_ids": list(
                narrative.conflict_ids
            ),
            "operator_notes": list(
                narrative.operator_notes
            ),
            "provider_name": (
                narrative.provider_name
            ),
            "model_name": (
                narrative.model_name
            ),
            "used_fallback": (
                narrative.used_fallback
            ),
            "metadata": dict(
                narrative.metadata
                or {}
            ),
        }
