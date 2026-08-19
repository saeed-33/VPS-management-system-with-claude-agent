"""
مشغل acceptance/evaluation ينفذ سيناريوهات readiness أو safety ويجمع نتائج قابلة للمراجعة.

الموقع في المعمارية: Acceptance tooling.
يُستدعى بواسطة: المشغل اليدوي أو CI.
يعتمد مباشرة على: app.core.contracts.investigation_read_models.
الحد المعماري: لا يغير policy الإنتاجية؛ ينفذ evaluation خارج runtime المعتاد.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass

from tools.acceptance.evaluation.contracts import (
    EvaluationMetric,
    EvaluationObservation,
)
from app.core.contracts.investigation_read_models.investigation_detail_read_model import InvestigationDetailReadModel


@dataclass(slots=True, frozen=True)
class PersistedRuntimeEvaluation:
    """
    يمثل PersistedRuntimeEvaluation جزءًا من طبقة Acceptance tooling.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه المشغل اليدوي أو CI. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    investigation_id: str
    observations: tuple[
        EvaluationObservation,
        ...
    ]


class PersistedRuntimeEvaluator:
    """
    Evaluate persisted runtime snapshots without re-running
    Specialists, SSH, tools, or the LLM.

    This evaluator only emits metrics that can be proven from
    persisted Investigation state.
    """

    def evaluate(
        self,
        investigation: InvestigationDetailReadModel,
    ) -> PersistedRuntimeEvaluation:
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

        تُستدعى عندما يصل المسار إلى evaluate؛ المدخلات المهمة: investigation.
        تعيد PersistedRuntimeEvaluation أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        if not investigation.runtime_available:
            return PersistedRuntimeEvaluation(
                investigation_id=(
                    investigation.investigation_id
                ),
                observations=(),
            )

        runtime = investigation.runtime

        if runtime is None:
            return PersistedRuntimeEvaluation(
                investigation_id=(
                    investigation.investigation_id
                ),
                observations=(),
            )

        observations = (
            self._specialist_completion(
                investigation
            ),
            self._evidence_grounding(
                investigation
            ),
            self._budget_compliance(
                investigation
            ),
            self._conflict_preservation(
                investigation
            ),
            self._final_diagnosis_grounding(
                investigation
            ),
        )

        return PersistedRuntimeEvaluation(
            investigation_id=(
                investigation.investigation_id
            ),
            observations=observations,
        )

    def _specialist_completion(
        self,
        investigation,
    ) -> EvaluationObservation:
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

        تُستدعى عندما يصل المسار إلى _specialist_completion؛ المدخلات المهمة: investigation.
        تعيد EvaluationObservation أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        runtime = investigation.runtime
        assert runtime is not None

        runs = tuple(
            item
            for item in runtime.specialist_runs
            if isinstance(item, dict)
        )

        passed = bool(runs) and all(
            item.get("status")
            == "completed"
            for item in runs
        )

        return EvaluationObservation(
            case_id=(
                f"persisted:"
                f"{investigation.investigation_id}:"
                "specialist-completion"
            ),
            metric=(
                EvaluationMetric
                .SPECIALIST_COMPLETION
            ),
            passed=passed,
            score=(
                1.0
                if passed
                else 0.0
            ),
            details=(
                f"{sum(1 for item in runs if item.get('status') == 'completed')}"
                f"/{len(runs)} Specialist runs completed."
            ),
            metadata={
                "investigation_id": (
                    investigation.investigation_id
                ),
                "source": "persisted-runtime",
            },
        )

    def _evidence_grounding(
        self,
        investigation,
    ) -> EvaluationObservation:
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

        تُستدعى عندما يصل المسار إلى _evidence_grounding؛ المدخلات المهمة: investigation.
        تعيد EvaluationObservation أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        runtime = investigation.runtime
        assert runtime is not None

        evidence_ids = {
            item.get("evidence_id")
            for item in runtime.evidence
            if isinstance(item, dict)
            and item.get("evidence_id")
        }

        referenced: set[str] = set()
        invalid_references: list[str] = []

        def collect_references(
            source: str,
            payload: dict,
        ) -> None:
            """
            ينفذ مرحلة الأداة أو يحفظ نتيجة التقييم ضمن طبقة Acceptance tooling.

            تُستدعى عندما يصل المسار إلى collect_references؛ المدخلات المهمة: source، payload.
            تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
            """
            values = payload.get("evidence_ids")

            if values is None:
                return

            if not isinstance(values, (list, tuple, set)):
                invalid_references.append(
                    f"{source}:not-a-list"
                )
                return

            for value in values:
                if not isinstance(value, str) or not value.strip():
                    invalid_references.append(
                        f"{source}:{value!r}"
                    )
                    continue
                referenced.add(value.strip())

        for index, run in enumerate(runtime.specialist_runs):
            if isinstance(run, dict):
                collect_references(
                    f"specialist_runs[{index}]",
                    run,
                )

        for index, claim in enumerate(runtime.correlated_claims):
            if isinstance(claim, dict):
                collect_references(
                    f"correlated_claims[{index}]",
                    claim,
                )

        for index, conflict in enumerate(runtime.conflicts):
            if isinstance(conflict, dict):
                collect_references(
                    f"conflicts[{index}]",
                    conflict,
                )

        final_diagnosis = (
            runtime.final_diagnosis
        )

        if isinstance(
            final_diagnosis,
            dict,
        ):
            collect_references(
                "final_diagnosis",
                final_diagnosis,
            )

        missing = sorted(
            referenced - evidence_ids
        )

        ownership_errors = []
        for item in runtime.evidence:
            if not isinstance(item, dict):
                ownership_errors.append("evidence:not-an-object")
                continue

            metadata = item.get("metadata")
            if not isinstance(metadata, dict):
                ownership_errors.append(
                    f"{item.get('evidence_id')}:missing-metadata"
                )
                continue

            evidence_investigation_id = metadata.get(
                "investigation_id"
            )
            if (
                evidence_investigation_id is not None
                and evidence_investigation_id
                != investigation.investigation_id
            ):
                ownership_errors.append(
                    f"{item.get('evidence_id')}:investigation"
                )

            evidence_server_id = metadata.get("server_id")
            if (
                evidence_server_id is not None
                and evidence_server_id != investigation.server_id
            ):
                ownership_errors.append(
                    f"{item.get('evidence_id')}:server"
                )

            evidence_report_id = metadata.get("report_id")
            if (
                evidence_report_id is not None
                and evidence_report_id != investigation.report_id
            ):
                ownership_errors.append(
                    f"{item.get('evidence_id')}:report"
                )

            kind = item.get("kind")
            if kind == "command_result" and evidence_server_id is None:
                ownership_errors.append(
                    f"{item.get('evidence_id')}:missing-server"
                )
            elif (
                kind in {"analysis", "monitoring_report"}
                and evidence_report_id is None
            ):
                ownership_errors.append(
                    f"{item.get('evidence_id')}:missing-report"
                )
            elif (
                kind not in {"analysis", "monitoring_report", "command_result"}
                and evidence_server_id is None
                and evidence_report_id is None
            ):
                ownership_errors.append(
                    f"{item.get('evidence_id')}:missing-context"
                )

        passed = not (
            missing
            or invalid_references
            or ownership_errors
        )

        detail_parts = []
        if missing:
            detail_parts.append(
                "missing=" + ",".join(missing)
            )
        if invalid_references:
            detail_parts.append(
                "invalid=" + ",".join(invalid_references)
            )
        if ownership_errors:
            detail_parts.append(
                "ownership=" + ",".join(ownership_errors)
            )

        return EvaluationObservation(
            case_id=(
                f"persisted:"
                f"{investigation.investigation_id}:"
                "evidence-grounding"
            ),
            metric=(
                EvaluationMetric
                .EVIDENCE_GROUNDING
            ),
            passed=passed,
            score=(
                1.0
                if passed
                else 0.0
            ),
            details=(
                "All referenced Evidence IDs are persisted "
                "and belong to the runtime context."
                if passed
                else "; ".join(detail_parts)
            ),
            metadata={
                "investigation_id": (
                    investigation.investigation_id
                ),
                "referenced_evidence_count": (
                    len(referenced)
                ),
                "persisted_evidence_count": (
                    len(evidence_ids)
                ),
                "invalid_reference_count": len(
                    invalid_references
                ),
                "ownership_error_count": len(
                    ownership_errors
                ),
                "source": "persisted-runtime",
            },
        )

    def _budget_compliance(
        self,
        investigation,
    ) -> EvaluationObservation:
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

        تُستدعى عندما يصل المسار إلى _budget_compliance؛ المدخلات المهمة: investigation.
        تعيد EvaluationObservation أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        runtime = investigation.runtime
        assert runtime is not None

        actions_used = (
            runtime.actions_used
            if runtime.actions_used is not None
            else 0
        )

        max_actions = (
            investigation.max_actions
        )

        passed = (
            actions_used <= max_actions
        )

        return EvaluationObservation(
            case_id=(
                f"persisted:"
                f"{investigation.investigation_id}:"
                "budget-compliance"
            ),
            metric=(
                EvaluationMetric
                .BUDGET_COMPLIANCE
            ),
            passed=passed,
            score=(
                1.0
                if passed
                else 0.0
            ),
            details=(
                f"{actions_used}/"
                f"{max_actions} actions used."
            ),
            metadata={
                "investigation_id": (
                    investigation.investigation_id
                ),
                "actions_used": actions_used,
                "max_actions": max_actions,
                "source": "persisted-runtime",
            },
        )

    def _conflict_preservation(
        self,
        investigation,
    ) -> EvaluationObservation:
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

        تُستدعى عندما يصل المسار إلى _conflict_preservation؛ المدخلات المهمة: investigation.
        تعيد EvaluationObservation أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        runtime = investigation.runtime
        assert runtime is not None

        conflicts = tuple(
            item
            for item in runtime.conflicts
            if isinstance(item, dict)
        )

        final_diagnosis = (
            runtime.final_diagnosis
        )

        narrative = runtime.narrative

        if not conflicts:
            passed = True
            details = (
                "No persisted conflict to preserve."
            )

        elif not isinstance(
            final_diagnosis,
            dict,
        ):
            passed = False
            details = (
                "Persisted conflicts exist but "
                "Final Diagnosis is missing."
            )

        else:
            persisted_conflict_ids = {
                item.get("conflict_id")
                for item in conflicts
                if item.get("conflict_id")
            }

            conflict_count = (
                final_diagnosis.get(
                    "conflict_count"
                )
            )

            narrative_ids = set()

            if isinstance(
                narrative,
                dict,
            ):
                narrative_ids.update(
                    narrative.get(
                        "conflict_ids"
                    )
                    or ()
                )

            count_preserved = (
                conflict_count
                == len(conflicts)
            )

            narrative_preserved = (
                not isinstance(
                    narrative,
                    dict,
                )
                or persisted_conflict_ids
                <= narrative_ids
            )

            passed = (
                count_preserved
                and narrative_preserved
            )

            details = (
                f"{len(conflicts)} persisted "
                "conflict(s); "
                f"diagnosis_count={conflict_count}; "
                f"narrative_refs="
                f"{len(narrative_ids)}."
            )

        return EvaluationObservation(
            case_id=(
                f"persisted:"
                f"{investigation.investigation_id}:"
                "conflict-preservation"
            ),
            metric=(
                EvaluationMetric
                .CONFLICT_PRESERVATION
            ),
            passed=passed,
            score=(
                1.0
                if passed
                else 0.0
            ),
            details=details,
            metadata={
                "investigation_id": (
                    investigation.investigation_id
                ),
                "conflict_count": (
                    len(conflicts)
                ),
                "source": "persisted-runtime",
            },
        )

    def _final_diagnosis_grounding(
        self,
        investigation,
    ) -> EvaluationObservation:
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

        تُستدعى عندما يصل المسار إلى _final_diagnosis_grounding؛ المدخلات المهمة: investigation.
        تعيد EvaluationObservation أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        runtime = investigation.runtime
        assert runtime is not None

        final_diagnosis = (
            runtime.final_diagnosis
        )

        narrative = runtime.narrative

        if not isinstance(
            final_diagnosis,
            dict,
        ):
            passed = False
            details = (
                "Final Diagnosis is missing."
            )

        else:
            persisted_claim_ids = {
                item.get("claim_id")
                for item
                in runtime.correlated_claims
                if isinstance(
                    item,
                    dict,
                )
                and item.get("claim_id")
            }

            persisted_conflict_ids = {
                item.get("conflict_id")
                for item
                in runtime.conflicts
                if isinstance(
                    item,
                    dict,
                )
                and item.get(
                    "conflict_id"
                )
            }

            if isinstance(
                narrative,
                dict,
            ):
                narrative_claim_ids = set(
                    narrative.get(
                        "claim_ids"
                    )
                    or ()
                )

                narrative_conflict_ids = set(
                    narrative.get(
                        "conflict_ids"
                    )
                    or ()
                )

                claims_valid = (
                    narrative_claim_ids
                    <= persisted_claim_ids
                )

                conflicts_valid = (
                    narrative_conflict_ids
                    <= persisted_conflict_ids
                )

            else:
                claims_valid = True
                conflicts_valid = True

            passed = (
                claims_valid
                and conflicts_valid
            )

            details = (
                "Narrative references only "
                "persisted Claim/Conflict IDs."
                if passed
                else (
                    "Narrative contains unknown "
                    "Claim/Conflict IDs."
                )
            )

        return EvaluationObservation(
            case_id=(
                f"persisted:"
                f"{investigation.investigation_id}:"
                "final-diagnosis-grounding"
            ),
            metric=(
                EvaluationMetric
                .FINAL_DIAGNOSIS_GROUNDING
            ),
            passed=passed,
            score=(
                1.0
                if passed
                else 0.0
            ),
            details=details,
            metadata={
                "investigation_id": (
                    investigation.investigation_id
                ),
                "source": "persisted-runtime",
            },
        )
