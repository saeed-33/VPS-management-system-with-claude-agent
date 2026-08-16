"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.remediation.autonomous_authorization_service، app.capabilities.remediation.autonomous_execution_service، app.capabilities.remediation.autonomous_policy_service، app.core.contracts.autonomous_remediation، app.core.contracts.remediation، app.core.utils.datetime.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from threading import Barrier, Thread
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.capabilities.remediation.autonomous_authorization_service import AutonomousAuthorizationService
from app.capabilities.remediation.autonomous_execution_service import AutonomousExecutionService
from app.capabilities.remediation.autonomous_policy_service import AutonomousPolicyService
from app.core.contracts.autonomous_remediation import (
    AutonomousDecisionOutcome,
    AutonomousHistorySnapshot,
    AutonomousPolicyDecision,
    AutonomousRemediationPolicy,
    AutonomousPolicyStatus,
)
from app.core.contracts.remediation import RemediationPlanStatus
from app.core.utils.datetime import utc_now
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.remediation import (
    AutonomousAuthorizationModel,
    AutonomousPolicyAuditEventModel,
    AutonomousPolicyDecisionModel,
    AutonomousPolicyExecutionReservationModel,
    AutonomousPolicyRuntimeStateModel,
    AutonomousRemediationPolicyModel,
    RemediationAuditEventModel,
    RemediationExecutionModel,
    RemediationPlanModel,
    RemediationRollbackModel,
)
from app.infrastructure.database.repositories.autonomous_remediation_repository import AutonomousRemediationRepository
from app.infrastructure.database.repositories.remediation_repository import RemediationRepository


TABLES = (
    RemediationPlanModel,
    RemediationExecutionModel,
    RemediationRollbackModel,
    RemediationAuditEventModel,
    AutonomousRemediationPolicyModel,
    AutonomousPolicyDecisionModel,
    AutonomousAuthorizationModel,
    AutonomousPolicyExecutionReservationModel,
    AutonomousPolicyRuntimeStateModel,
    AutonomousPolicyAuditEventModel,
)


def make_harness(tmp_path: Path, *, mode: str = "failure"):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_harness؛ المدخلات المهمة: tmp_path، mode.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    engine = create_engine(
        f"sqlite:///{tmp_path / 'phase7-breaker.db'}",
        connect_args={"check_same_thread": False, "timeout": 30},
    )
    Base.metadata.create_all(engine, tables=[model.__table__ for model in TABLES])
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    repository = AutonomousRemediationRepository(factory)
    remediation_repository = RemediationRepository(factory)
    policy_service = AutonomousPolicyService(repository=repository)
    policy = policy_service.create(
        policy_id="policy-1", name="nginx breaker", status="enabled",
        issue_fingerprint="issue-1", allowed_action_type="start_service",
        allowed_target_pattern="nginx", maximum_risk="low", max_consecutive_failures=1,
        auto_suspend_on_failure=True, max_executions_per_hour=20, max_executions_per_day=20,
    )
    plan = SimpleNamespace(
        plan_id="plan-1", plan_fingerprint="plan-fp-1", server_id=4,
        status=RemediationPlanStatus.SANDBOX_PASSED.value,
        plan_metadata={"issue_fingerprint": "issue-1"}, risk_level="low",
        diagnosis_claim_ids=["claim-1"], evidence_ids=["evidence-1"],
        proposed_actions=[{"id": "start-nginx", "action_type": "start_service", "target": "nginx"}],
    )
    with factory() as session:
        session.add(RemediationPlanModel(
            plan_id=plan.plan_id, investigation_id="investigation-1", server_id=4,
            title="Start nginx", problem_summary="nginx is inactive", proposed_actions=plan.proposed_actions,
            diagnosis_claim_ids=plan.diagnosis_claim_ids, evidence_ids=plan.evidence_ids,
            risk_level="low", plan_version=1, plan_fingerprint=plan.plan_fingerprint,
            status=plan.status, plan_metadata=plan.plan_metadata,
        ))
        session.commit()
    controlled = ControlledRemediation(factory, plan, mode)
    authorization_service = AutonomousAuthorizationService(repository=repository)
    history = AutonomousHistorySnapshot(issue_fingerprint="issue-1", action_type="start_service", target="nginx")
    service = AutonomousExecutionService(
        repository=repository, remediation_repository=controlled, remediation_service=controlled,
        policy_service=policy_service, history_service=SimpleNamespace(snapshot=lambda **_: history),
        candidate_service=SimpleNamespace(), authorization_service=authorization_service,
        automatic_remediation_allowed=True,
    )

    def deterministic_evaluate(*, plan_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى deterministic_evaluate؛ المدخلات المهمة: plan_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        current = repository.get_policy(policy.policy_id)
        contract = policy_service._model_to_contract(current)
        if not service._automatic_remediation_allowed:
            outcome = AutonomousDecisionOutcome.DENY
            reasons = ("global_autonomy_disabled",)
        elif current.status == AutonomousPolicyStatus.SUSPENDED.value:
            outcome = AutonomousDecisionOutcome.DENY
            reasons = ("policy_suspended",)
        elif current.status == AutonomousPolicyStatus.DISABLED.value:
            outcome = AutonomousDecisionOutcome.DENY
            reasons = ("policy_disabled",)
        else:
            outcome = AutonomousDecisionOutcome.AUTO_EXECUTE
            reasons = ("policy_match",)
        decision = AutonomousPolicyDecision(
            decision_id=str(uuid4()), outcome=outcome, reason_codes=reasons,
            human_readable_reasons=reasons, policy_id=contract.policy_id,
            policy_version=contract.version, plan_id=plan.plan_id,
            plan_fingerprint=plan.plan_fingerprint, issue_fingerprint="issue-1",
            server_id=4, action_type="start_service", target="nginx",
        )
        repository.create_decision(decision, history={}, metadata={})
        sandbox = controlled.get_latest_sandbox_validation(plan_id)
        return decision, plan, SimpleNamespace(action_id="start-nginx", action_type="start_service", target="nginx"), contract, sandbox, history

    service.evaluate = deterministic_evaluate
    return service, repository, policy_service, controlled, factory, policy


class ControlledRemediation:
    """
    يمثل ControlledRemediation جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, factory, plan, mode):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: factory، plan، mode.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.factory = factory
        self.plan = plan
        self.mode = mode
        self.audit_events = []
        self.apply_calls = 0
        self.rollback_calls = 0

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
            validation_id="sandbox-1", status="passed", plan_id=self.plan.plan_id,
            plan_fingerprint=self.plan.plan_fingerprint, server_id=4, service="nginx",
            action_type="start_service", before_evidence_ids=["before"],
            after_evidence_ids=["after"], verification_status="verified",
            created_at=utc_now(),
        )

    get_sandbox_validation = get_latest_sandbox_validation

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
        with self.factory() as session:
            return session.scalar(select(RemediationExecutionModel).where(RemediationExecutionModel.execution_id == execution_id))

    def audit_autonomous(self, *, plan_id, event_type, payload):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى audit_autonomous؛ المدخلات المهمة: plan_id، event_type، payload.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.audit_events.append(event_type)
        RemediationRepository(self.factory).append_audit_event(
            plan_id=plan_id, event_type=event_type, actor="autonomous-policy", payload=payload,
        )

    def apply_approved(self, *, plan_id, server_id, actor, idempotency_key, autonomous_authorization):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى apply_approved؛ المدخلات المهمة: plan_id، server_id، actor، idempotency_key، autonomous_authorization.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.apply_calls += 1
        execution_id = f"execution-{self.apply_calls}"
        if self.mode == "success":
            status, applied = "succeeded", True
        else:
            status, applied = "failed", False
        if self.mode == "verification_failure":
            status = "succeeded"
        with self.factory() as session:
            session.add(RemediationExecutionModel(
                execution_id=execution_id, plan_id=plan_id, action_id="start-nginx", server_id=server_id,
                status=status, idempotency_key=idempotency_key, before_evidence_ids=["before"],
                after_evidence_ids=["after"], stdout="", stderr="", error=None,
                execution_metadata={"autonomous": True, "mode": self.mode}, completed_at=utc_now(),
            ))
            session.commit()
        if self.mode == "verification_failure":
            self.audit_autonomous(plan_id=plan_id, event_type="verification_failed", payload={"execution_id": execution_id})
        return {"applied": applied, "execution_id": execution_id}

    def rollback(self, *, plan_id, execution_id, actor, server_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى rollback؛ المدخلات المهمة: plan_id، execution_id، actor، server_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.rollback_calls += 1
        failed = self.mode == "rollback_failure"
        with self.factory() as session:
            session.add(RemediationRollbackModel(
                rollback_id=f"rollback-{self.rollback_calls}", execution_id=execution_id,
                status="failed" if failed else "succeeded", before_evidence_ids=["before"],
                after_evidence_ids=["after"], details={"controlled": True},
            ))
            session.commit()
        event = "rollback_failed" if failed else "rollback_succeeded"
        self.audit_autonomous(plan_id=plan_id, event_type=event, payload={"execution_id": execution_id})
        return {"rolled_back": not failed, "execution_id": execution_id}


def test_success_does_not_trip_and_failure_persists_all_links(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_success_does_not_trip_and_failure_persists_all_links؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, repo, _policy_service, controlled, factory, policy = make_harness(tmp_path, mode="success")
    result = service.attempt(plan_id="plan-1", idempotency_key="success-key")
    runtime = repo.get_runtime_state(policy.policy_id)
    assert result["outcome"] == "auto_execute"
    assert controlled.apply_calls == 1
    assert repo.get_policy(policy.policy_id).status == "enabled"
    assert runtime.consecutive_failures == 0

    failure_path = tmp_path / "failure"
    failure_path.mkdir()
    service2, repo2, _policy_service2, controlled2, factory2, policy2 = make_harness(failure_path)
    failure = service2.attempt(plan_id="plan-1", idempotency_key="failure-key")
    runtime2 = repo2.get_runtime_state(policy2.policy_id)
    reservation = repo2.get_reservation_by_idempotency_key("failure-key")
    assert failure["result"]["applied"] is False
    assert reservation.status == "failed" and reservation.execution_id == "execution-1"
    assert repo2.get_policy(policy2.policy_id).status == "suspended"
    assert runtime2.consecutive_failures == 1
    assert runtime2.triggering_execution_id == "execution-1"
    assert repo2.get_decision(failure["decision"].decision_id).policy_version == 1
    assert repo2.get_authorization(reservation.authorization_id).status == "consumed"
    fresh_repository = AutonomousRemediationRepository(factory2)
    assert fresh_repository.get_policy(policy2.policy_id).status == "suspended"
    assert fresh_repository.get_runtime_state(policy2.policy_id).consecutive_failures == 1
    assert repo2.list_policy_audit_events(policy2.policy_id) == []
    assert {
        "autonomous_runtime_failure_recorded", "autonomous_circuit_breaker_tripped", "autonomous_policy_suspended",
    }.issubset(set(controlled2.audit_events))


def test_suspended_policy_blocks_next_and_operator_resume_starts_new_epoch(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_suspended_policy_blocks_next_and_operator_resume_starts_new_epoch؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, repo, policy_service, controlled, _factory, policy = make_harness(tmp_path)
    service.attempt(plan_id="plan-1", idempotency_key="first")
    denied = service.attempt(plan_id="plan-1", idempotency_key="second")
    assert denied["outcome"] == "deny"
    assert denied["decision"].reason_codes == ("policy_suspended",)
    assert controlled.apply_calls == 1
    assert repo.get_reservation_by_idempotency_key("second") is None

    service._automatic_remediation_allowed = False
    global_denied = service.attempt(plan_id="plan-1", idempotency_key="global-after-failure")
    assert global_denied["decision"].reason_codes == ("global_autonomy_disabled",)
    service._automatic_remediation_allowed = True
    policy_denied = service.attempt(plan_id="plan-1", idempotency_key="policy-after-failure")
    assert policy_denied["decision"].reason_codes == ("policy_suspended",)
    assert controlled.apply_calls == 1

    resumed = policy_service.resume(policy.policy_id)
    assert resumed.status == "enabled"
    assert repo.get_runtime_state(policy.policy_id).consecutive_failures == 0
    assert "autonomous_execution_finalized" in controlled.audit_events
    assert [event.event_type for event in repo.list_policy_audit_events(policy.policy_id)] == ["autonomous_policy_resumed"]

    controlled.mode = "success"
    success = service.attempt(plan_id="plan-1", idempotency_key="after-resume")
    assert success["result"]["applied"] is True
    assert repo.get_policy(policy.policy_id).status == "enabled"
    assert repo.get_runtime_state(policy.policy_id).consecutive_failures == 0
    assert controlled.audit_events.count("autonomous_execution_finalized") >= 2


def test_second_failure_after_resume_and_verification_rollback_fail_closed(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_second_failure_after_resume_and_verification_rollback_fail_closed؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, repo, policy_service, controlled, _factory, policy = make_harness(tmp_path, mode="verification_failure")
    service.attempt(plan_id="plan-1", idempotency_key="first")
    assert controlled.rollback_calls == 1
    assert repo.get_policy(policy.policy_id).status == "suspended"
    policy_service.resume(policy.policy_id)
    controlled.mode = "rollback_failure"
    result = service.attempt(plan_id="plan-1", idempotency_key="second")
    assert result["result"]["applied"] is False
    assert result["result"]["autonomous_rollback"]["rolled_back"] is False
    assert repo.get_policy(policy.policy_id).status == "suspended"
    assert repo.get_runtime_state(policy.policy_id).consecutive_failures == 1
    assert "verification_failed" in controlled.audit_events
    assert "rollback_failed" in controlled.audit_events


def test_prewrite_denial_does_not_count_and_global_gate_is_independent(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_prewrite_denial_does_not_count_and_global_gate_is_independent؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, repo, policy_service, controlled, _factory, policy = make_harness(tmp_path)
    service._automatic_remediation_allowed = False
    denied = service.attempt(plan_id="plan-1", idempotency_key="denied")
    assert denied["decision"].reason_codes == ("global_autonomy_disabled",)
    assert repo.get_runtime_state(policy.policy_id).consecutive_failures == 0
    assert controlled.apply_calls == 0
    policy_service.disable(policy.policy_id)
    service._automatic_remediation_allowed = True
    denied_policy = service.attempt(plan_id="plan-1", idempotency_key="policy-disabled")
    assert denied_policy["outcome"] == "deny"
    assert controlled.apply_calls == 0
    assert repo.get_runtime_state(policy.policy_id).consecutive_failures == 0


def test_recovery_failure_is_counted_once_and_concurrent_accounting_is_idempotent(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_recovery_failure_is_counted_once_and_concurrent_accounting_is_idempotent؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, repo, _policy_service, controlled, factory, policy = make_harness(tmp_path)
    decision = AutonomousPolicyDecision(
        decision_id="recovery-decision", outcome=AutonomousDecisionOutcome.AUTO_EXECUTE,
        reason_codes=("policy_match",), human_readable_reasons=("ok",), policy_id=policy.policy_id,
        policy_version=1, plan_id="plan-1", plan_fingerprint="plan-fp-1", issue_fingerprint="issue-1",
        server_id=4, action_type="start_service", target="nginx",
    )
    repo.create_decision(decision, history={}, metadata={})
    authorization = AutonomousAuthorizationService(repository=repo).issue(decision=decision, sandbox_validation_id="sandbox-1")
    reservation = repo.reserve(
        idempotency_key="recovery", owner_token="owner", policy_id=policy.policy_id, plan_id="plan-1",
        plan_fingerprint="plan-fp-1", action_type="start_service", target="nginx", server_id=4,
        now=utc_now() - timedelta(hours=1), lease_seconds=1,
    )
    repo.update_reservation_authorization(reservation.reservation_id, owner_token="owner", authorization_id=authorization.authorization_id)
    AutonomousAuthorizationService(repository=repo).consume(authorization.authorization_id)
    recovered = service.attempt(plan_id="plan-1", idempotency_key="recovery")
    repeated = service.attempt(plan_id="plan-1", idempotency_key="recovery")
    assert recovered["outcome"] == "deny" and repeated["outcome"] == "deny"
    assert repo.get_runtime_state(policy.policy_id).consecutive_failures == 1
    assert controlled.apply_calls == 0

    policy_service = AutonomousPolicyService(repository=repo)
    policy_service.resume(policy.policy_id)
    barrier = Barrier(2)
    results = []

    def count_failure():
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى count_failure؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        barrier.wait()
        results.append(repo.record_autonomous_failure(
            policy_id=policy.policy_id, policy_version=1, failure_key="same-failure",
            decision_id="recovery-decision", execution_id="execution-same",
        ))

    threads = [Thread(target=count_failure) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sum(item[1] for item in results) == 1
    assert repo.get_runtime_state(policy.policy_id).consecutive_failures == 1


def test_old_policy_version_failure_cannot_rewrite_new_epoch(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_old_policy_version_failure_cannot_rewrite_new_epoch؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _service, repo, policy_service, _controlled, _factory, policy = make_harness(tmp_path)
    first = repo.record_autonomous_failure(
        policy_id=policy.policy_id, policy_version=1, failure_key="old-failure", decision_id="old-decision",
    )
    assert first[1] is True
    policy_service.update(policy.policy_id, name="nginx breaker v2")
    runtime, counted, _tripped, stale = repo.record_autonomous_failure(
        policy_id=policy.policy_id, policy_version=1, failure_key="late-old-failure", decision_id="old-decision",
    )
    assert counted is False and stale is True
    assert runtime.consecutive_failures == 1
    assert repo.get_policy(policy.policy_id).version == 2
