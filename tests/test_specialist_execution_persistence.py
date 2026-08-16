"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.investigation.runtime_snapshot_service، app.capabilities.investigation.specialist_execution_service، app.capabilities.investigation.specialist_investigation_loop، app.core.contracts.investigation.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

from types import SimpleNamespace

import asyncio

from app.capabilities.investigation.runtime_snapshot_service import (
    InvestigationRuntimeSnapshotService,
)
from app.capabilities.investigation.specialist_execution_service import (
    SpecialistExecutionService,
)
from app.capabilities.investigation.specialist_investigation_loop import (
    SpecialistInvestigationLoopResult,
    SpecialistLoopStopReason,
)
from app.core.contracts.investigation import (
    EvidenceKind,
    EvidenceReference,
    SpecialistResult,
    SpecialistTask,
    SpecialistTaskStatus,
    InvestigationFinding,
)


class Repository:
    """
    يمثل Repository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.model = SimpleNamespace(
            investigation_id="inv-1",
            server_id=4,
            report_id=1832,
            analysis_id=1,
            status="created",
            max_specialists=3,
            max_rounds=2,
            max_actions=6,
            investigation_metadata={
                "runtime_snapshot": {
                    "status": "investigating",
                    "actions_used": 0,
                    "specialist_runs": [],
                    "evidence": [],
                    "metadata": {},
                }
            },
        )
        self.reservations = {}

    def reserve_specialist(self, *, investigation_id, specialist_slug, ownership_token, lease_seconds=900):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى reserve_specialist؛ المدخلات المهمة: investigation_id، specialist_slug، ownership_token، lease_seconds.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        runs = self.model.investigation_metadata["runtime_snapshot"]["specialist_runs"]
        existing = next((item for item in runs if item["specialist_slug"] == specialist_slug), None)
        if existing and existing["status"] in {"completed", "failed", "cancelled"}:
            return {"status": "completed", "run": existing, "actions_used": 1}
        if specialist_slug in self.reservations:
            return {"status": "in_progress", "owner": self.reservations[specialist_slug]}
        self.reservations[specialist_slug] = ownership_token
        return {"status": "reserved", "ownership_token": ownership_token, "actions_used": 1}

    def finalize_specialist(self, *, investigation_id, specialist_slug, ownership_token, merge):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى finalize_specialist؛ المدخلات المهمة: investigation_id، specialist_slug، ownership_token، merge.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        assert self.reservations.pop(specialist_slug, None) == ownership_token
        status, metadata = merge(self.model, dict(self.model.investigation_metadata))
        self.model.status = status
        self.model.investigation_metadata = metadata
        return self.model

    def persist_finalization(self, *, investigation_id, merge):
        """
        ينفذ مرحلة الأداة أو يحفظ نتيجة التقييم ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى persist_finalization؛ المدخلات المهمة: investigation_id، merge.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        status, metadata = merge(self.model, dict(self.model.investigation_metadata))
        self.model.status = status
        self.model.investigation_metadata = metadata
        return self.model


def task(slug):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى task؛ المدخلات المهمة: slug.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SpecialistTask(
        task_id=f"inv-1:{slug}:1",
        investigation_id="inv-1",
        server_id=4,
        report_id=1832,
        specialist_id=slug,
        objective=f"Investigate {slug}",
        status=SpecialistTaskStatus.RUNNING,
    )


def loop_result(
    slug,
    *,
    actions=1,
    status=SpecialistTaskStatus.COMPLETED,
    with_finding=False,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى loop_result؛ المدخلات المهمة: slug، actions، status، with_finding.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    evidence = EvidenceReference(
        evidence_id=f"ev-{slug}",
        kind=EvidenceKind.COMMAND_RESULT,
        title=f"{slug} evidence",
    )
    findings = (
        InvestigationFinding(
            finding_id=f"finding-{slug}",
            title=f"{slug} finding",
            description=f"{slug} finding description",
            confidence=0.9,
            evidence_ids=(evidence.evidence_id,),
            metadata={"diagnostic_state": "present"},
        ),
    ) if with_finding and status == SpecialistTaskStatus.COMPLETED else ()
    result = SpecialistResult(
        task_id=f"inv-1:{slug}:1",
        specialist_id=slug,
        status=status,
        summary=f"{slug} result",
        confidence=0.9 if status == SpecialistTaskStatus.COMPLETED else 0.0,
        findings=findings,
        evidence_ids=(evidence.evidence_id,) if status == SpecialistTaskStatus.COMPLETED else (),
    )
    return SpecialistInvestigationLoopResult(
        final_result=result,
        evidence=(evidence,) if status == SpecialistTaskStatus.COMPLETED else (),
        rounds_completed=1,
        actions_executed=actions,
        investigation_actions_used=actions,
        stop_reason=SpecialistLoopStopReason.COMPLETED,
        provider="ollama",
        model="test-model",
        traces=(),
    )


def test_specialist_runs_accumulate_and_duplicate_is_idempotent():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_specialist_runs_accumulate_and_duplicate_is_idempotent؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repository = Repository()
    service = SpecialistExecutionService(
        repository=repository,
        snapshot_service=InvestigationRuntimeSnapshotService(repository),
    )

    for slug in ("systemd-service", "docker"):
        reservation = service.reserve_with_token(investigation_id="inv-1", specialist_slug=slug)
        asyncio.run(service.finalize(
            task=task(slug),
            loop_result=loop_result(slug),
            selected_specialists=("systemd-service", "docker", "linux-network"),
            ownership_token=reservation["ownership_token"],
        ))

    snapshot = repository.model.investigation_metadata["runtime_snapshot"]
    assert [item["specialist_slug"] for item in snapshot["specialist_runs"]] == [
        "systemd-service", "docker"
    ]
    assert snapshot["actions_used"] == 1
    assert snapshot["metadata"]["remaining_specialists"] == ["linux-network"]
    assert snapshot["runtime_available"] is True
    assert snapshot["final_diagnosis_available"] is False

    duplicate = service.reserve_with_token(investigation_id="inv-1", specialist_slug="systemd-service")
    assert duplicate["status"] == "completed"
    assert len(snapshot["specialist_runs"]) == 2
    assert len(snapshot["evidence"]) == 2


def test_all_selected_specialists_trigger_atomic_aggregate_finalization():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_all_selected_specialists_trigger_atomic_aggregate_finalization؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repository = Repository()
    service = SpecialistExecutionService(
        repository=repository,
        snapshot_service=InvestigationRuntimeSnapshotService(repository),
    )
    selected = ("systemd-service", "docker", "linux-network")

    for slug in selected:
        reservation = service.reserve_with_token(
            investigation_id="inv-1",
            specialist_slug=slug,
        )
        asyncio.run(service.finalize(
            task=task(slug),
            loop_result=loop_result(slug, with_finding=True),
            selected_specialists=selected,
            ownership_token=reservation["ownership_token"],
        ))

    snapshot = repository.model.investigation_metadata["runtime_snapshot"]
    assert snapshot["status"] == "completed"
    assert snapshot["runtime_available"] is True
    assert snapshot["final_diagnosis_available"] is True
    assert snapshot["correlated_claims"]
    assert snapshot["narrative"]["summary"]


def test_second_concurrent_reservation_is_blocked():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_second_concurrent_reservation_is_blocked؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repository = Repository()
    first = repository.reserve_specialist(
        investigation_id="inv-1",
        specialist_slug="docker",
        ownership_token="owner-a",
    )
    second = repository.reserve_specialist(
        investigation_id="inv-1",
        specialist_slug="docker",
        ownership_token="owner-b",
    )
    assert first["status"] == "reserved"
    assert second["status"] == "in_progress"


def test_failed_specialist_is_persisted_without_claiming_runtime_available():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_failed_specialist_is_persisted_without_claiming_runtime_available؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repository = Repository()
    service = SpecialistExecutionService(
        repository=repository,
        snapshot_service=InvestigationRuntimeSnapshotService(repository),
    )
    reservation = service.reserve_with_token(
        investigation_id="inv-1",
        specialist_slug="systemd-service",
    )

    asyncio.run(service.finalize(
        task=task("systemd-service"),
        loop_result=loop_result(
            "systemd-service",
            status=SpecialistTaskStatus.FAILED,
        ),
        selected_specialists=("systemd-service", "docker"),
        ownership_token=reservation["ownership_token"],
    ))

    snapshot = repository.model.investigation_metadata["runtime_snapshot"]
    assert snapshot["runtime_available"] is False
    assert snapshot["final_diagnosis_available"] is False
    assert snapshot["metadata"]["failed_specialists"] == [
        "systemd-service"
    ]
