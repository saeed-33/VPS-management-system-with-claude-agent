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
from app.core.ports.investigation.investigation_repository import InvestigationRepositoryPort


from .runtime_snapshot_serializer import InvestigationRuntimeSnapshotSerializer
from .runtime_snapshot_merger import InvestigationRuntimeSnapshotMerger


class InvestigationRuntimeSnapshotService:
    """
    يدير إنشاء ودمج وحفظ لقطات تقدم التحقيق.
    """

    SNAPSHOT_VERSION = "4.19.2-v1"

    def __init__(
        self,
        repository: InvestigationRepositoryPort,
    ) -> None:
        """
        يهيئ InvestigationRuntimeSnapshotService ويربط الاعتماديات اللازمة لدورة التحقيق.
        """
        self._repository = repository
        self._serializer = InvestigationRuntimeSnapshotSerializer()
        self._merger = InvestigationRuntimeSnapshotMerger(
            snapshot_version=self.SNAPSHOT_VERSION,
            serializer=self._serializer,
        )

    def persist(
        self,
        *,
        investigation_id: str,
        execution_result: InvestigationExecutionResult,
        final_diagnosis: FinalDiagnosis | None = None,
        narrative: FinalDiagnosisNarrative | None = None,
    ):
        """
        يحفظ لقطة تشغيل التحقيق بعد التحقق من ارتباطها.
        """
        if not investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )

        runtime_id = (
            execution_result
            .state
            .investigation_id
        )

        snapshot = self.build_snapshot(
            execution_result=execution_result,
            final_diagnosis=final_diagnosis,
            narrative=narrative,
        )

        def merge(model, metadata):
            """
            يدمج اللقطة الجديدة مع اللقطة المحفوظة داخل بيانات النموذج.
            """
            current = dict(metadata.get("runtime_snapshot") or {})
            if current:
                snapshot["specialist_runs"] = self._merge_by_key(
                    current.get("specialist_runs", []),
                    snapshot.get("specialist_runs", []),
                    key="task_id",
                )
                snapshot["evidence"] = self._merge_by_key(
                    current.get("evidence", []),
                    snapshot.get("evidence", []),
                    key="evidence_id",
                )
                snapshot["evidence_count"] = len(snapshot["evidence"])
                snapshot["actions_used"] = max(
                    int(current.get("actions_used") or 0),
                    int(snapshot.get("actions_used") or 0),
                )
                for key in ("correlated_claims", "conflicts", "final_diagnosis", "narrative"):
                    if not snapshot.get(key) and current.get(key):
                        snapshot[key] = current[key]
                snapshot["metadata"] = {
                    **dict(current.get("metadata") or {}),
                    **dict(snapshot.get("metadata") or {}),
                }
            metadata["runtime_snapshot"] = self._serializer.json_safe(snapshot)
            metadata["runtime_snapshot_version"] = self.SNAPSHOT_VERSION
            metadata["runtime_investigation_id"] = runtime_id
            return metadata

        if hasattr(self._repository, "merge_runtime_snapshot"):
            return self._repository.merge_runtime_snapshot(
                investigation_id=investigation_id,
                status=execution_result.state.status.value,
                merge=merge,
            )

        # قد لا تعرض البدائل القديمة إلا طريقة الدمج السابقة، أما المسار الفعلي
        # فيثبت تحديث الحالة بقفل يمنع فقدان نتيجة متزامنة.
        model = self._repository.get_by_investigation_id(investigation_id)
        if model is None:
            raise ValueError(f"Investigation not found: {investigation_id}")
        return self._repository.update_runtime_snapshot(
            investigation_id=investigation_id,
            status=execution_result.state.status.value,
            metadata=merge(model, dict(model.investigation_metadata or {})),
        )

    @staticmethod
    def _merge_by_key(existing: list, incoming: list, *, key: str) -> list:
        """
        يدمج عناصر اللقطة مع إزالة التكرار حسب مفتاح ثابت.
        """
        merged = {item.get(key): dict(item) for item in existing if isinstance(item, dict) and item.get(key)}
        for item in incoming:
            if isinstance(item, dict) and item.get(key):
                merged[item[key]] = dict(item)
        return list(merged.values())

    def build_snapshot(
        self,
        *,
        execution_result: InvestigationExecutionResult,
        final_diagnosis: FinalDiagnosis | None = None,
        narrative: FinalDiagnosisNarrative | None = None,
    ) -> dict:
        """
        يبني لقطة أولية من بيانات التحقيق ونتائج الاختصاصيين.
        """
        state = execution_result.state

        specialist_runs = tuple(
            self._serializer._serialize_run(run)
            for run in execution_result.runs
        )

        evidence = tuple(
            self._serializer._serialize_evidence(
                item,
                investigation_id=state.investigation_id,
                server_id=state.server_id,
                report_id=state.report_id,
            )
            for item in state.evidence
        )

        snapshot = {
            "version": self.SNAPSHOT_VERSION,
            "status": state.status.value,
            "orchestrator": (
                state.metadata.get(
                    "orchestrator"
                )
            ),
            "execution_mode": (
                state.metadata.get(
                    "execution_mode"
                )
            ),
            "waves_completed": (
                state.metadata.get(
                    "waves_completed"
                )
            ),
            "actions_used": (
                execution_result
                .investigation_actions_used
            ),
            "evidence_count": len(evidence),
            "specialist_runs": list(
                specialist_runs
            ),
            "evidence": list(evidence),
            "correlated_claims": [],
            "conflicts": [],
            "final_diagnosis": None,
            "narrative": None,
            "metadata": {
                "executed_specialists": list(
                    state.metadata.get(
                        "executed_specialists",
                        (),
                    )
                ),
                "secondary_requested": list(
                    state.metadata.get(
                        "secondary_requested",
                        (),
                    )
                ),
                "secondary_accepted": list(
                    state.metadata.get(
                        "secondary_accepted",
                        (),
                    )
                ),
                "max_specialists": (
                    state.budget.max_specialists
                ),
                "max_rounds": (
                    state.budget.max_rounds
                ),
                "max_actions": (
                    state.budget.max_actions
                ),
            },
        }

        if final_diagnosis is not None:
            snapshot[
                "correlated_claims"
            ] = [
                self._serializer._serialize_claim(claim)
                for claim
                in final_diagnosis.claims
            ]

            snapshot["conflicts"] = [
                self._serializer._serialize_conflict(
                    conflict
                )
                for conflict
                in final_diagnosis.conflicts
            ]

            snapshot[
                "final_diagnosis"
            ] = self._serializer._serialize_final_diagnosis(
                final_diagnosis
            )

        if narrative is not None:
            snapshot[
                "narrative"
            ] = self._serializer._serialize_narrative(
                narrative
            )

        return self._serializer.json_safe(snapshot)

    def merge_specialist_result(
        self,
        *,
        model,
        metadata: dict,
        task,
        loop_result,
        selected_specialists: tuple[str, ...],
    ) -> tuple[str, dict]:
        """يدمج نتيجة اختصاصي في لقطة التحقيق."""
        return self._merger.merge_specialist_result(
            model=model,
            metadata=metadata,
            task=task,
            loop_result=loop_result,
            selected_specialists=selected_specialists,
        )

    def merge_finalization(
        self,
        *,
        metadata: dict,
        final_diagnosis: FinalDiagnosis,
        narrative: FinalDiagnosisNarrative,
    ) -> tuple[str, dict]:
        """يدمج التشخيص النهائي والسرد في اللقطة."""
        return self._merger.merge_finalization(
            metadata=metadata,
            final_diagnosis=final_diagnosis,
            narrative=narrative,
        )

    def _serialize_claim(self, claim) -> dict:
        """يحافظ على واجهة القراءة القديمة أثناء تفويض التسلسل للمكوّن المختص."""
        return self._serializer._serialize_claim(claim)

    def _serialize_final_diagnosis(self, final_diagnosis) -> dict:
        """يحافظ على واجهة القراءة القديمة أثناء تفويض التسلسل للمكوّن المختص."""
        return self._serializer._serialize_final_diagnosis(final_diagnosis)
