"""Tests for test autonomous concurrency recovery.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.remediation.autonomous_execution_service، app.core.contracts.autonomous_remediation، app.core.contracts.remediation، app.infrastructure.database.base، app.infrastructure.database.models.remediation، app.infrastructure.database.repositories.autonomous_remediation_repository.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Barrier, Lock, Thread
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.capabilities.remediation.autonomous_execution_service.autonomous_execution_service import AutonomousExecutionService
from app.core.contracts.autonomous_remediation.autonomous_authorization import AutonomousAuthorization
from app.core.contracts.autonomous_remediation.autonomous_authorization_status import AutonomousAuthorizationStatus
from app.core.contracts.autonomous_remediation.autonomous_decision_outcome import AutonomousDecisionOutcome
from app.core.contracts.autonomous_remediation.autonomous_history_snapshot import AutonomousHistorySnapshot
from app.core.contracts.remediation.remediation_plan_status import RemediationPlanStatus
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.remediation.autonomous_authorization import AutonomousAuthorizationModel
from app.infrastructure.database.models.remediation.autonomous_decision import AutonomousPolicyDecisionModel
from app.infrastructure.database.models.remediation.autonomous_reservation import AutonomousPolicyExecutionReservationModel
from app.infrastructure.database.models.remediation.autonomous_runtime import AutonomousPolicyRuntimeStateModel
from app.infrastructure.database.models.remediation.execution import RemediationExecutionModel
from app.infrastructure.database.models.remediation.plan import RemediationPlanModel
from app.infrastructure.database.repositories.autonomous_remediation_repository.repository import AutonomousRemediationRepository


NOW = datetime(2026, 8, 14, tzinfo=timezone.utc)
TABLES = (
    RemediationPlanModel,
    RemediationExecutionModel,
    AutonomousPolicyDecisionModel,
    AutonomousAuthorizationModel,
    AutonomousPolicyExecutionReservationModel,
    AutonomousPolicyRuntimeStateModel,
)


def make_database(tmp_path: Path):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_database؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    engine = create_engine(
        f"sqlite:///{tmp_path / 'phase7-concurrency.db'}",
        connect_args={"check_same_thread": False, "timeout": 30},
    )
    Base.metadata.create_all(engine, tables=[model.__table__ for model in TABLES])
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, factory, AutonomousRemediationRepository(factory)


def add_plan(factory, *, plan_id="plan-1", fingerprint="plan-fp-1"):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى add_plan؛ المدخلات المهمة: factory، plan_id، fingerprint.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    with factory() as session:
        session.add(RemediationPlanModel(
            plan_id=plan_id,
            investigation_id="investigation-1",
            server_id=4,
            title="Start nginx",
            problem_summary="nginx is inactive",
            proposed_actions=[{"id": "start-nginx", "action_type": "start_service", "target": "nginx"}],
            diagnosis_claim_ids=["claim-1"],
            evidence_ids=["evidence-1"],
            risk_level="low",
            plan_version=1,
            plan_fingerprint=fingerprint,
            status=RemediationPlanStatus.SANDBOX_PASSED.value,
            plan_metadata={"issue_fingerprint": "issue-1"},
            created_at=NOW,
            updated_at=NOW,
        ))
        session.commit()


def add_execution(factory, *, execution_id="execution-1", key="key-1", status="succeeded"):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى add_execution؛ المدخلات المهمة: factory، execution_id، key، status.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    with factory() as session:
        session.add(RemediationExecutionModel(
            execution_id=execution_id,
            plan_id="plan-1",
            action_id="start-nginx",
            server_id=4,
            status=status,
            idempotency_key=key,
            before_evidence_ids=["before"],
            after_evidence_ids=["after"],
            stdout="",
            stderr="",
            execution_metadata={"autonomous": True},
            created_at=NOW,
            completed_at=NOW,
        ))
        session.commit()


def add_authorization(repo, *, authorization_id="authorization-1", status=AutonomousAuthorizationStatus.VALID):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى add_authorization؛ المدخلات المهمة: repo، authorization_id، status.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    authorization = AutonomousAuthorization(
        authorization_id=authorization_id,
        token=f"token-{authorization_id}",
        status=status,
        policy_id="policy-1",
        policy_version=1,
        decision_id="decision-1",
        plan_id="plan-1",
        plan_fingerprint="plan-fp-1",
        server_id=4,
        action_type="start_service",
        target="nginx",
        sandbox_validation_id="sandbox-1",
        issued_at=NOW,
        expires_at=NOW + timedelta(hours=1),
    )
    repo.create_authorization(authorization)
    return authorization


def reserve(repo, *, key="key-1", owner="owner-1", now=NOW, lease_seconds=900):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى reserve؛ المدخلات المهمة: repo، key، owner، now، lease_seconds.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return repo.reserve(
        idempotency_key=key,
        owner_token=owner,
        policy_id="policy-1",
        plan_id="plan-1",
        plan_fingerprint="plan-fp-1",
        action_type="start_service",
        target="nginx",
        server_id=4,
        now=now,
        lease_seconds=lease_seconds,
    )


def test_atomic_same_key_race_has_one_database_reservation(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_atomic_same_key_race_has_one_database_reservation؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    barrier = Barrier(2)
    results = []
    errors = []

    def worker(owner):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى worker؛ المدخلات المهمة: owner.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        try:
            barrier.wait()
            item = reserve(repo, owner=owner)
            results.append((owner, item.reservation_id, item.status))
        except Exception as exc:  # pragma: no cover - diagnostic assertion below
            errors.append(exc)

    threads = [Thread(target=worker, args=(f"owner-{index}",)) for index in (1, 2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert len(results) == 2
    assert {item[1] for item in results}.__len__() == 1
    with factory() as session:
        rows = list(session.scalars(select(AutonomousPolicyExecutionReservationModel)).all())
    assert len(rows) == 1

    owner = rows[0].owner_token
    repo.finalize_reservation(rows[0].reservation_id, owner_token=owner, status="completed", execution_id="execution-1")
    assert len(repo.list_reservations(plan_id="plan-1")) == 1


def test_service_same_key_race_has_one_authorization_and_execution_path(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_service_same_key_race_has_one_authorization_and_execution_path؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    service, auth, remediation, _policy = make_service(repo)
    barrier = Barrier(2)
    results = []
    errors = []

    def worker():
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى worker؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        try:
            barrier.wait()
            results.append(service.attempt(plan_id="plan-1", idempotency_key="key-1"))
        except Exception as exc:  # pragma: no cover - diagnostic assertion below
            errors.append(exc)

    threads = [Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert len(repo.list_reservations(plan_id="plan-1")) == 1
    assert auth.issue_calls == 1
    assert remediation.apply_calls == 1
    assert sum(result.get("idempotent") is not True for result in results) == 1
    assert any(result.get("outcome") in {"in_progress", "auto_execute"} for result in results)


def test_different_keys_cannot_execute_same_active_or_completed_operation(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_different_keys_cannot_execute_same_active_or_completed_operation؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo, key="key-a", owner="owner-a")
    competing = reserve(repo, key="key-b", owner="owner-b")

    assert competing.status == "in_progress"
    assert competing.idempotency_key == "key-a"
    repo.finalize_reservation(first.reservation_id, owner_token="owner-a", status="completed", execution_id="execution-a")

    replay = reserve(repo, key="key-b", owner="owner-b", now=NOW + timedelta(seconds=1))
    assert replay.reservation_id == first.reservation_id
    assert replay.idempotency_key == "key-a"
    assert len(repo.list_reservations(plan_id="plan-1")) == 1


def test_owner_token_protects_authorization_finalize_and_competing_state(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_owner_token_protects_authorization_finalize_and_competing_state؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo, owner="owner-a")

    with pytest.raises(ValueError, match="owned by another worker"):
        repo.update_reservation_authorization(first.reservation_id, owner_token="owner-b", authorization_id="auth-b")
    with pytest.raises(ValueError, match="owned by another worker"):
        repo.finalize_reservation(first.reservation_id, owner_token="owner-b", status="completed", execution_id="execution-b")

    competing = reserve(repo, key="key-b", owner="owner-b")
    persisted = repo.get_reservation_by_idempotency_key("key-1")
    assert competing.status == "in_progress"
    assert persisted.status == "reserved"
    assert persisted.owner_token == "owner-a"


def test_reserved_and_in_progress_replay_fail_closed_without_mutation(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_reserved_and_in_progress_replay_fail_closed_without_mutation؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo)
    replay = repo.get_reservation_by_idempotency_key("key-1")
    assert replay.reservation_id == first.reservation_id
    assert replay.status == "reserved"
    assert repo.get_reservation_by_idempotency_key("key-1").status == "reserved"

    competing = reserve(repo, key="key-2", owner="owner-2")
    assert competing.status == "in_progress"
    assert repo.get_reservation_by_idempotency_key("key-1").status == "reserved"


def test_completed_replay_preserves_terminal_identity(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_completed_replay_preserves_terminal_identity؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo)
    add_execution(factory, key="key-1")
    repo.finalize_reservation(first.reservation_id, owner_token="owner-1", status="completed", execution_id="execution-1")

    replay = reserve(repo, now=NOW + timedelta(seconds=1))
    assert replay.status == "completed"
    assert replay.reservation_id == first.reservation_id
    assert replay.execution_id == "execution-1"


def test_failed_terminal_reservation_is_not_automatically_retried(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_failed_terminal_reservation_is_not_automatically_retried؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo)
    repo.finalize_reservation(first.reservation_id, owner_token="owner-1", status="failed")

    replay = reserve(repo, now=NOW + timedelta(seconds=1))
    assert replay.status == "failed"
    assert replay.reservation_id == first.reservation_id
    assert len(repo.list_reservations(plan_id="plan-1")) == 1


def test_stale_lease_recovery_before_authorization_reuses_reservation(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_stale_lease_recovery_before_authorization_reuses_reservation؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo, now=NOW, lease_seconds=1)

    recovered = reserve(repo, owner="owner-2", now=NOW + timedelta(seconds=2), lease_seconds=900)

    assert recovered.reservation_id == first.reservation_id
    assert recovered.status == "reserved"
    assert recovered.owner_token == "owner-2"
    assert recovered.authorization_id is None
    assert recovered.execution_id is None


def test_crash_after_authorization_issued_preserves_single_authorization(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_crash_after_authorization_issued_preserves_single_authorization؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo, now=NOW, lease_seconds=1)
    authorization = add_authorization(repo)
    repo.update_reservation_authorization(first.reservation_id, owner_token="owner-1", authorization_id=authorization.authorization_id)

    recovered = reserve(repo, owner="owner-2", now=NOW + timedelta(seconds=2))

    assert recovered.status == "reserved"
    assert recovered.authorization_id == authorization.authorization_id
    assert recovered.owner_token == "owner-2"
    repo.consume_authorization(authorization.authorization_id, now=NOW + timedelta(seconds=2))
    with pytest.raises(ValueError, match="not valid"):
        repo.consume_authorization(authorization.authorization_id, now=NOW + timedelta(seconds=3))


def test_crash_after_authorization_consumed_without_execution_fails_closed(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_crash_after_authorization_consumed_without_execution_fails_closed؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo, now=NOW, lease_seconds=1)
    authorization = add_authorization(repo)
    repo.update_reservation_authorization(first.reservation_id, owner_token="owner-1", authorization_id=authorization.authorization_id)
    repo.consume_authorization(authorization.authorization_id, now=NOW)

    recovered = reserve(repo, owner="owner-2", now=NOW + timedelta(seconds=2))

    assert recovered.status == "failed"
    assert recovered.execution_id is None
    assert len(repo.list_reservations(plan_id="plan-1")) == 1


def test_crash_after_write_before_finalize_reconciles_existing_execution(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_crash_after_write_before_finalize_reconciles_existing_execution؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo, now=NOW, lease_seconds=1)
    authorization = add_authorization(repo, status=AutonomousAuthorizationStatus.CONSUMED)
    repo.update_reservation_authorization(first.reservation_id, owner_token="owner-1", authorization_id=authorization.authorization_id)
    add_execution(factory, key="key-1", execution_id="execution-after-write")

    recovered = reserve(repo, owner="owner-2", now=NOW + timedelta(seconds=2))

    assert recovered.status == "completed"
    assert recovered.execution_id == "execution-after-write"
    assert len(repo.list_reservations(plan_id="plan-1")) == 1


def test_concurrent_stale_recovery_has_one_takeover(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_concurrent_stale_recovery_has_one_takeover؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo, now=NOW, lease_seconds=1)
    barrier = Barrier(2)
    results = []
    errors = []

    def worker(owner):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى worker؛ المدخلات المهمة: owner.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        try:
            barrier.wait()
            results.append(reserve(repo, owner=owner, now=NOW + timedelta(seconds=2)))
        except Exception as exc:  # pragma: no cover - diagnostic assertion below
            errors.append(exc)

    threads = [Thread(target=worker, args=(f"owner-{index}",)) for index in (2, 3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert {item.reservation_id for item in results} == {first.reservation_id}
    assert sorted(item.status for item in results) == ["in_progress", "reserved"]
    persisted = repo.get_reservation_by_idempotency_key("key-1")
    assert persisted.status == "reserved"
    assert persisted.owner_token in {"owner-2", "owner-3"}


def test_plan_fingerprint_change_cannot_recover_old_reservation(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_plan_fingerprint_change_cannot_recover_old_reservation؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    reserve(repo, now=NOW, lease_seconds=1)

    with pytest.raises(ValueError, match="different autonomous operation"):
        repo.reserve(
            idempotency_key="key-1", owner_token="owner-2", policy_id="policy-1",
            plan_id="plan-1", plan_fingerprint="new-plan-fp", action_type="start_service",
            target="nginx", server_id=4, now=NOW + timedelta(seconds=2), lease_seconds=900,
        )

    persisted = repo.get_reservation_by_idempotency_key("key-1")
    assert persisted.plan_fingerprint == "plan-fp-1"
    assert persisted.owner_token == "owner-1"


class FakeAuthorizationService:
    """
    يمثل FakeAuthorizationService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.authorization = None
        self.issue_calls = 0
        self.consume_calls = 0
        self._lock = Lock()

    def issue(self, *, decision, sandbox_validation_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى issue؛ المدخلات المهمة: decision، sandbox_validation_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        with self._lock:
            self.issue_calls += 1
            self.authorization = SimpleNamespace(
                authorization_id=f"authorization-{self.issue_calls}",
                policy_id=decision.policy_id,
                policy_version=decision.policy_version,
                decision_id=decision.decision_id,
                plan_id=decision.plan_id,
                plan_fingerprint=decision.plan_fingerprint,
                server_id=decision.server_id,
                action_type=decision.action_type,
                target=decision.target,
                sandbox_validation_id=sandbox_validation_id,
                status="valid",
            )
            return self.authorization

    def get(self, authorization_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get؛ المدخلات المهمة: authorization_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        assert self.authorization is not None
        assert self.authorization.authorization_id == authorization_id
        return self.authorization

    def consume(self, authorization_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى consume؛ المدخلات المهمة: authorization_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        with self._lock:
            self.consume_calls += 1
            assert self.authorization.authorization_id == authorization_id
            if self.authorization.status != "valid":
                raise ValueError("Autonomous authorization is not valid.")
            self.authorization.status = "consumed"
            return self.authorization


class FakeRemediationRepository:
    """
    يمثل FakeRemediationRepository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, plan):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: plan.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.plan = plan
        self.executions = {}

    def get_plan(self, plan_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_plan؛ المدخلات المهمة: plan_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.plan if plan_id == self.plan.plan_id else None

    def get_latest_sandbox_validation(self, _plan_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_latest_sandbox_validation؛ المدخلات المهمة: _plan_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return SimpleNamespace(
            validation_id="sandbox-1", status="passed", plan_id="plan-1",
            plan_fingerprint="plan-fp-1", server_id=4, service="nginx",
            action_type="start_service", before_evidence_ids=["before"],
            after_evidence_ids=["after"], verification_status="verified", created_at=NOW,
        )

    def get_sandbox_validation(self, _validation_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_sandbox_validation؛ المدخلات المهمة: _validation_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.get_latest_sandbox_validation("plan-1")

    def sandbox_evidence_belongs(self, **_kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى sandbox_evidence_belongs؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return True

    def get_execution(self, *, execution_id=None, **_kwargs):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_execution؛ المدخلات المهمة: execution_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.executions.get(execution_id)


class FakeRemediationService:
    """
    يمثل FakeRemediationService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, remediation_repository):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: remediation_repository.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.repository = remediation_repository
        self.apply_calls = 0
        self.audit_events = []
        self._lock = Lock()

    def audit_autonomous(self, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى audit_autonomous؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.audit_events.append(kwargs)

    def apply_approved(self, *, plan_id, server_id, actor, idempotency_key, autonomous_authorization):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى apply_approved؛ المدخلات المهمة: plan_id، server_id، actor، idempotency_key، autonomous_authorization.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        with self._lock:
            self.apply_calls += 1
            execution = SimpleNamespace(
                execution_id=f"execution-{self.apply_calls}",
                idempotency_key=idempotency_key,
                plan_id=plan_id,
                server_id=server_id,
                action_id="start-nginx",
                status="succeeded",
            )
            self.repository.executions[execution.execution_id] = execution
            return {"applied": True, "execution_id": execution.execution_id}


def make_service(repo, *, automatic=True, policy_version=1):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_service؛ المدخلات المهمة: repo، automatic، policy_version.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    plan = SimpleNamespace(
        plan_id="plan-1", plan_fingerprint="plan-fp-1", server_id=4,
        status=RemediationPlanStatus.SANDBOX_PASSED.value,
        plan_metadata={"issue_fingerprint": "issue-1"}, risk_level="low",
        diagnosis_claim_ids=["claim-1"], evidence_ids=["evidence-1"],
        proposed_actions=[{"id": "start-nginx", "action_type": "start_service", "target": "nginx"}],
    )
    remediation_repository = FakeRemediationRepository(plan)
    remediation_service = FakeRemediationService(remediation_repository)
    authorization_service = FakeAuthorizationService()
    policy = SimpleNamespace(policy_id="policy-1", version=policy_version, status="enabled", auto_suspend_on_failure=False)
    decision = SimpleNamespace(
        decision_id="decision-1", outcome=AutonomousDecisionOutcome.AUTO_EXECUTE,
        policy_id="policy-1", policy_version=1, plan_id="plan-1", plan_fingerprint="plan-fp-1",
        issue_fingerprint="issue-1", server_id=4, action_type="start_service", target="nginx",
    )
    repo.get_policy = lambda _policy_id: policy
    service = AutonomousExecutionService(
        repository=repo,
        remediation_repository=remediation_repository,
        remediation_service=remediation_service,
        policy_service=SimpleNamespace(suspend=lambda *args, **kwargs: None),
        history_service=SimpleNamespace(snapshot=lambda **kwargs: AutonomousHistorySnapshot(**kwargs)),
        candidate_service=SimpleNamespace(),
        authorization_service=authorization_service,
        automatic_remediation_allowed=automatic,
    )
    service.evaluate = lambda **kwargs: (
        decision,
        plan,
        SimpleNamespace(action_id="start-nginx", action_type="start_service", target="nginx"),
        policy,
        remediation_repository.get_latest_sandbox_validation("plan-1"),
        AutonomousHistorySnapshot(issue_fingerprint="issue-1", action_type="start_service", target="nginx"),
    )
    return service, authorization_service, remediation_service, policy


def test_service_recovery_reuses_authorization_and_audits_recovery(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_service_recovery_reuses_authorization_and_audits_recovery؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    reserve(repo, now=NOW, lease_seconds=1)
    service, authorization, remediation, _policy = make_service(repo)

    result = service.attempt(plan_id="plan-1", idempotency_key="key-1")

    assert result["outcome"] == "auto_execute"
    assert authorization.issue_calls == 1
    assert authorization.consume_calls == 1
    assert remediation.apply_calls == 1
    assert any(item["event_type"] == "autonomous_reservation_recovered" for item in remediation.audit_events)


def test_service_recovery_after_auth_issued_does_not_issue_a_second_authorization(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_service_recovery_after_auth_issued_does_not_issue_a_second_authorization؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo, now=NOW, lease_seconds=1)
    service, authorization, remediation, _policy = make_service(repo)
    existing = authorization.issue(
        decision=SimpleNamespace(
            policy_id="policy-1", policy_version=1, decision_id="decision-1", plan_id="plan-1",
            plan_fingerprint="plan-fp-1", server_id=4, action_type="start_service", target="nginx",
        ),
        sandbox_validation_id="sandbox-1",
    )
    repo.update_reservation_authorization(first.reservation_id, owner_token="owner-1", authorization_id=existing.authorization_id)
    authorization.issue_calls = 0

    result = service.attempt(plan_id="plan-1", idempotency_key="key-1")

    assert result["outcome"] == "auto_execute"
    assert authorization.issue_calls == 0
    assert authorization.consume_calls == 1
    assert remediation.apply_calls == 1


def test_kill_switch_blocks_stale_recovery_before_reservation_mutation(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_kill_switch_blocks_stale_recovery_before_reservation_mutation؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo, now=NOW, lease_seconds=1)
    service, authorization, remediation, _policy = make_service(repo, automatic=False)
    denied = SimpleNamespace(
        decision_id="decision-disabled", outcome=AutonomousDecisionOutcome.DENY,
        reason_codes=("global_autonomy_disabled",), policy_id=None, policy_version=None,
        plan_id="plan-1", plan_fingerprint="plan-fp-1", issue_fingerprint="issue-1",
        server_id=4, action_type="start_service", target="nginx",
    )
    service.evaluate = lambda **kwargs: (
        denied, service._remediation_repository.plan,
        SimpleNamespace(action_id="start-nginx", action_type="start_service", target="nginx"),
        None, service._remediation_repository.get_latest_sandbox_validation("plan-1"),
        AutonomousHistorySnapshot(issue_fingerprint="issue-1", action_type="start_service", target="nginx"),
    )

    result = service.attempt(plan_id="plan-1", idempotency_key="key-1")

    assert result["outcome"] == "deny"
    assert result["decision"].reason_codes == ("global_autonomy_disabled",)
    assert authorization.issue_calls == 0
    assert remediation.apply_calls == 0
    persisted = repo.get_reservation_by_idempotency_key("key-1")
    assert persisted.reservation_id == first.reservation_id
    assert persisted.owner_token == "owner-1"


def test_policy_version_change_fails_closed_during_recovery(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_policy_version_change_fails_closed_during_recovery؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _engine, factory, repo = make_database(tmp_path)
    add_plan(factory)
    first = reserve(repo, now=NOW, lease_seconds=1)
    service, authorization, remediation, policy = make_service(repo, policy_version=2)
    existing = authorization.issue(
        decision=SimpleNamespace(
            policy_id="policy-1", policy_version=1, decision_id="decision-1", plan_id="plan-1",
            plan_fingerprint="plan-fp-1", server_id=4, action_type="start_service", target="nginx",
        ),
        sandbox_validation_id="sandbox-1",
    )
    repo.update_reservation_authorization(first.reservation_id, owner_token="owner-1", authorization_id=existing.authorization_id)
    authorization.issue_calls = 0

    result = service.attempt(plan_id="plan-1", idempotency_key="key-1")

    assert result["outcome"] == "deny"
    assert result["error"] == "authorization_stale:policy_version"
    assert authorization.issue_calls == 0
    assert remediation.apply_calls == 0
