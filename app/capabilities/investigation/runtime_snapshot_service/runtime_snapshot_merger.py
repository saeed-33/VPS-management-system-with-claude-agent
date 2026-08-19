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
from app.infrastructure.database.repositories.investigation_repository.repository import InvestigationRepository


from .runtime_snapshot_serializer import InvestigationRuntimeSnapshotSerializer


from .runtime_snapshot_serializer import InvestigationRuntimeSnapshotSerializer

class InvestigationRuntimeSnapshotMerger:
    """ينسق دمج نتائج الاختصاصيين والتشخيص النهائي في اللقطة."""

    def __init__(
        self,
        *,
        snapshot_version: str,
        serializer: InvestigationRuntimeSnapshotSerializer,
    ) -> None:
        self._snapshot_version = snapshot_version
        self._serializer = serializer

    def merge_specialist_result(
        self,
        *,
        model,
        metadata: dict,
        task,
        loop_result,
        selected_specialists: tuple[str, ...],
    ) -> tuple[str, dict]:
        """
        يدمج نتيجة اختصاصي في لقطة التحقيق.
        """
        merged = dict(metadata)
        snapshot = dict(merged.get("runtime_snapshot") or {})
        if not snapshot:
            snapshot = self._empty_snapshot(model)

        runs = list(snapshot.get("specialist_runs") or [])
        if any(item.get("specialist_slug") == task.specialist_id for item in runs):
            return str(model.status), merged

        evidence = list(snapshot.get("evidence") or [])
        evidence_by_id = {item.get("evidence_id"): item for item in evidence}
        for item in loop_result.evidence:
            evidence_by_id[item.evidence_id] = self._serializer._serialize_evidence(
                item,
                investigation_id=model.investigation_id,
                server_id=model.server_id,
                report_id=model.report_id,
            )

        runs.append(self._serializer._serialize_accepted_run(task, loop_result))
        snapshot["specialist_runs"] = runs
        snapshot["evidence"] = list(evidence_by_id.values())
        snapshot["evidence_count"] = len(snapshot["evidence"])
        snapshot["actions_used"] = max(
            int(snapshot.get("actions_used") or 0),
            int(loop_result.investigation_actions_used),
        )
        all_terminal = all(
            any(
                item.get("specialist_slug") == slug
                and item.get("status") in {"completed", "failed", "cancelled"}
                for item in runs
            )
            for slug in selected_specialists
        )
        has_failure = any(item.get("status") in {"failed", "cancelled"} for item in runs)
        has_findings = any(
            item.get("status") == "completed"
            and bool(item.get("findings"))
            for item in runs
        )
        snapshot["status"] = (
            "failed" if all_terminal and has_failure
            else "completed" if all_terminal and has_findings
            else "waiting_for_evidence" if all_terminal
            else "investigating"
        )

        runtime_metadata = dict(snapshot.get("metadata") or {})
        terminal = [
            item.get("specialist_slug")
            for item in runs
            if item.get("status") in {"completed", "failed", "cancelled"}
        ]
        completed = [
            item.get("specialist_slug")
            for item in runs
            if item.get("status") == "completed"
        ]
        failed = [
            item.get("specialist_slug")
            for item in runs
            if item.get("status") in {"failed", "cancelled"}
        ]
        runtime_metadata["selected_specialists"] = list(selected_specialists)
        runtime_metadata["completed_specialists"] = list(dict.fromkeys(completed))
        runtime_metadata["terminal_specialists"] = list(dict.fromkeys(terminal))
        runtime_metadata["failed_specialists"] = list(dict.fromkeys(failed))
        runtime_metadata["remaining_specialists"] = [
            slug for slug in selected_specialists if slug not in terminal
        ]
        runtime_metadata["executed_specialists"] = list(dict.fromkeys(terminal))
        snapshot["metadata"] = runtime_metadata
        # نحفظ الحجز الفاشل أو الملغى لاستمرار السجل، لكنه لا يعد نتيجة متخصصة؛
        # لا نرفع حالة الاكتمال إلا بعد تثبيت تشغيل متخصص واحد على الأقل.
        snapshot["runtime_available"] = bool(completed)
        snapshot["final_diagnosis_available"] = isinstance(snapshot.get("final_diagnosis"), dict)
        merged["runtime_snapshot"] = self._serializer._json_safe(snapshot)
        merged["runtime_snapshot_version"] = self._snapshot_version
        merged["runtime_investigation_id"] = model.investigation_id
        return snapshot["status"], merged

    def merge_finalization(
        self,
        *,
        metadata: dict,
        final_diagnosis: FinalDiagnosis,
        narrative: FinalDiagnosisNarrative,
    ) -> tuple[str, dict]:
        """
        يدمج التشخيص النهائي والسرد في اللقطة.
        """
        merged = dict(metadata)
        snapshot = dict(merged.get("runtime_snapshot") or {})
        snapshot["correlated_claims"] = [self._serializer._serialize_claim(item) for item in final_diagnosis.claims]
        snapshot["conflicts"] = [self._serializer._serialize_conflict(item) for item in final_diagnosis.conflicts]
        snapshot["final_diagnosis"] = self._serializer._serialize_final_diagnosis(final_diagnosis)
        snapshot["narrative"] = self._serializer._serialize_narrative(narrative)
        snapshot["runtime_available"] = True
        snapshot["final_diagnosis_available"] = True
        snapshot["status"] = "completed"
        merged["runtime_snapshot"] = self._serializer._json_safe(snapshot)
        merged["runtime_snapshot_version"] = self._snapshot_version
        return "completed", merged

    def _empty_snapshot(self, model) -> dict:
        """
        ينشئ لقطة فارغة ببنية التحقيق المتوقعة.
        """
        return {
            "version": self._snapshot_version,
            "status": "investigating",
            "actions_used": 0,
            "evidence_count": 0,
            "specialist_runs": [],
            "evidence": [],
            "correlated_claims": [],
            "conflicts": [],
            "final_diagnosis": None,
            "narrative": None,
            "runtime_available": False,
            "final_diagnosis_available": False,
            "metadata": {
                "max_specialists": model.max_specialists,
                "max_rounds": model.max_rounds,
                "max_actions": model.max_actions,
            },
        }
