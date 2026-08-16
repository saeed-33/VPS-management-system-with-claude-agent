"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.remediation.autonomous_execution_service، app.core.contracts.autonomous_remediation، app.core.contracts.remediation.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock, Thread
from types import SimpleNamespace

import pytest

from app.capabilities.remediation.autonomous_execution_service import (
    AutonomousExecutionService,
)
from app.core.contracts.autonomous_remediation import (
    AutonomousDecisionOutcome,
    AutonomousHistorySnapshot,
    AutonomousPolicyStatus,
)
from app.core.contracts.remediation import RemediationPlanStatus


NOW = datetime.now(timezone.utc)


class FakeReservationRepository:
    """
    يمثل FakeReservationRepository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.reservations = {}
        self.authorizations = 0
        self.execution_reservations = 0
        self._lock = Lock()

    def get_reservation_by_idempotency_key(self, key):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_reservation_by_idempotency_key؛ المدخلات المهمة: key.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        with self._lock:
            return self.reservations.get(key)

    def matching_policies(self, **_kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى matching_policies؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return []

    def get_policy(self, policy_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_policy؛ المدخلات المهمة: policy_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return SimpleNamespace(policy_id=policy_id, version=1, status="enabled")

    def execution_counts(self, **_kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى execution_counts؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return {"hour": 0, "day": 0, "last": None}

    def get_runtime_state(self, policy_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_runtime_state؛ المدخلات المهمة: policy_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return SimpleNamespace(consecutive_failures=0, policy_id=policy_id)

    def list_reservations(self, **_kwargs):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_reservations؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return []

    def create_decision(self, *args, **kwargs):
        """
        يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى create_decision؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return SimpleNamespace()

    def reserve(self, *, idempotency_key, owner_token, policy_id, plan_id,
                plan_fingerprint, action_type, target, server_id, now):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى reserve؛ المدخلات المهمة: idempotency_key، owner_token، policy_id، plan_id، plan_fingerprint، action_type.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        with self._lock:
            existing = self.reservations.get(idempotency_key)
            if existing is not None:
                if existing.status == "reserved":
                    existing.status = "in_progress"
                return existing
            reservation = SimpleNamespace(
                reservation_id=f"reservation-{len(self.reservations) + 1}",
                idempotency_key=idempotency_key, owner_token=owner_token,
                policy_id=policy_id, plan_id=plan_id,
                plan_fingerprint=plan_fingerprint, action_type=action_type,
                target=target, server_id=server_id, status="reserved",
                authorization_id=None, execution_id=None,
            )
            self.reservations[idempotency_key] = reservation
            self.execution_reservations += 1
            return reservation

    def update_reservation_authorization(self, reservation_id, *, owner_token, authorization_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى update_reservation_authorization؛ المدخلات المهمة: reservation_id، owner_token، authorization_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        reservation = next(item for item in self.reservations.values() if item.reservation_id == reservation_id)
        assert reservation.owner_token == owner_token
        reservation.authorization_id = authorization_id
        return reservation

    def finalize_reservation(self, reservation_id, *, owner_token, status, execution_id=None):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى finalize_reservation؛ المدخلات المهمة: reservation_id، owner_token، status، execution_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        reservation = next(item for item in self.reservations.values() if item.reservation_id == reservation_id)
        assert reservation.owner_token == owner_token
        reservation.status = status
        reservation.execution_id = execution_id
        return reservation

    def update_runtime_state(self, *args, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى update_runtime_state؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return SimpleNamespace()


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
        return self.plan if self.plan.plan_id == plan_id else None

    def get_latest_sandbox_validation(self, _plan_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_latest_sandbox_validation؛ المدخلات المهمة: _plan_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return SimpleNamespace(
            validation_id="sandbox-1", status="passed",
            plan_id=self.plan.plan_id, plan_fingerprint=self.plan.plan_fingerprint,
            server_id=self.plan.server_id, service="nginx", action_type="start_service",
            before_evidence_ids=["before"], after_evidence_ids=["after"],
            verification_status="verified", created_at=NOW,
        )

    def get_sandbox_validation(self, _validation_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_sandbox_validation؛ المدخلات المهمة: _validation_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.get_latest_sandbox_validation(self.plan.plan_id)

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
    def __init__(self, repository):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: repository.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.repository = repository
        self.apply_calls = 0

    def audit_autonomous(self, **_kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى audit_autonomous؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return None

    def apply_approved(self, *, plan_id, server_id, actor, idempotency_key, autonomous_authorization):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى apply_approved؛ المدخلات المهمة: plan_id، server_id، actor، idempotency_key، autonomous_authorization.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.apply_calls += 1
        execution = SimpleNamespace(
            execution_id=f"execution-{self.apply_calls}",
            idempotency_key=idempotency_key, plan_id=plan_id,
            server_id=server_id, action_id="start-nginx", status="succeeded",
        )
        self.repository.executions[execution.execution_id] = execution
        return {"applied": True, "execution_id": execution.execution_id}


class FakePolicyService:
    """
    يمثل FakePolicyService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def _model_to_contract(self, model):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى _model_to_contract؛ المدخلات المهمة: model.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return model


class FakeAuthorizationService:
    """
    يمثل FakeAuthorizationService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, repository):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: repository.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.repository = repository
        self.issue_calls = 0
        self.consume_calls = 0
        self.authorization = None

    def issue(self, *, decision, sandbox_validation_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى issue؛ المدخلات المهمة: decision، sandbox_validation_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.issue_calls += 1
        self.authorization = SimpleNamespace(
            authorization_id=f"authorization-{self.issue_calls}",
            policy_id=decision.policy_id, policy_version=1,
            decision_id=decision.decision_id,
            plan_id=decision.plan_id, plan_fingerprint=decision.plan_fingerprint,
            server_id=decision.server_id, action_type=decision.action_type,
            target=decision.target, sandbox_validation_id=sandbox_validation_id,
            status="consumed",
        )
        return self.authorization

    def consume(self, authorization_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى consume؛ المدخلات المهمة: authorization_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.consume_calls += 1
        assert self.authorization.authorization_id == authorization_id
        return self.authorization


def make_plan(**updates):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_plan؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    values = {
        "plan_id": "plan-1", "plan_fingerprint": "fingerprint-1", "server_id": 4,
        "status": RemediationPlanStatus.SANDBOX_PASSED.value,
        "plan_metadata": {"issue_fingerprint": "issue-1"},
        "proposed_actions": [{
            "id": "start-nginx", "action_type": "start_service", "target": "nginx",
        }],
        "risk_level": "low", "diagnosis_claim_ids": ["claim"], "evidence_ids": ["evidence"],
    }
    values.update(updates)
    return SimpleNamespace(**values)


def make_service(*, plan=None):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_service؛ المدخلات المهمة: plan.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    plan = plan or make_plan()
    reservation_repository = FakeReservationRepository()
    remediation_repository = FakeRemediationRepository(plan)
    remediation_service = FakeRemediationService(remediation_repository)
    authorization_service = FakeAuthorizationService(reservation_repository)
    decision = SimpleNamespace(
        outcome=AutonomousDecisionOutcome.AUTO_EXECUTE,
        policy_id="policy-1", policy_version=1, plan_id=plan.plan_id,
        plan_fingerprint=plan.plan_fingerprint, issue_fingerprint="issue-1",
        server_id=plan.server_id, action_type="start_service", target="nginx",
        decision_id="decision-1",
    )
    service = AutonomousExecutionService(
        repository=reservation_repository,
        remediation_repository=remediation_repository,
        remediation_service=remediation_service,
        policy_service=FakePolicyService(),
        history_service=SimpleNamespace(snapshot=lambda **kwargs: AutonomousHistorySnapshot(**kwargs)),
        candidate_service=SimpleNamespace(),
        authorization_service=authorization_service,
        automatic_remediation_allowed=True,
    )
    service.evaluate_calls = 0

    def fake_evaluate(*, plan_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى fake_evaluate؛ المدخلات المهمة: plan_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        service.evaluate_calls += 1
        return (
            decision,
            plan,
            SimpleNamespace(action_id="start-nginx", action_type="start_service", target="nginx"),
            SimpleNamespace(policy_id="policy-1", status=AutonomousPolicyStatus.ENABLED, auto_suspend_on_failure=False),
            remediation_repository.get_latest_sandbox_validation(plan_id),
            AutonomousHistorySnapshot(issue_fingerprint="issue-1", action_type="start_service", target="nginx"),
        )

    service.evaluate = fake_evaluate
    return service, reservation_repository, remediation_service, authorization_service, remediation_repository


def test_first_attempt_creates_one_reservation_authorization_and_execution():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_first_attempt_creates_one_reservation_authorization_and_execution؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, reservations, remediation, authorization, _ = make_service()

    result = service.attempt(plan_id="plan-1", idempotency_key="key-1")

    assert result["outcome"] == "auto_execute"
    assert len(reservations.reservations) == 1
    assert reservations.execution_reservations == 1
    assert authorization.issue_calls == 1
    assert authorization.consume_calls == 1
    assert remediation.apply_calls == 1
    assert service.evaluate_calls == 1


def test_completed_replay_returns_same_terminal_identity_without_reexecution():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_completed_replay_returns_same_terminal_identity_without_reexecution؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, reservations, remediation, authorization, remediation_repository = make_service()
    first = service.attempt(plan_id="plan-1", idempotency_key="key-1")
    reservation = reservations.reservations["key-1"]
    execution_id = first["result"]["execution_id"]

    replay = service.attempt(plan_id="plan-1", idempotency_key="key-1")

    assert replay["idempotent"] is True
    assert replay["reservation"]["reservation_id"] == reservation.reservation_id
    assert replay["execution_id"] == execution_id
    assert replay["execution"].execution_id == execution_id
    assert authorization.issue_calls == 1
    assert authorization.consume_calls == 1
    assert remediation.apply_calls == 1
    assert len(reservations.reservations) == 1
    assert len(remediation_repository.executions) == 1
    assert service.evaluate_calls == 1


def test_in_progress_replay_is_deterministic_without_execution():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_in_progress_replay_is_deterministic_without_execution؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, reservations, remediation, authorization, _ = make_service()
    reservation = SimpleNamespace(
        reservation_id="reservation-1", idempotency_key="key-1", owner_token="owner",
        policy_id="policy-1", plan_id="plan-1", plan_fingerprint="fingerprint-1",
        action_type="start_service", target="nginx", server_id=4, status="in_progress",
        authorization_id=None, execution_id=None,
    )
    reservations.reservations["key-1"] = reservation

    result = service.attempt(plan_id="plan-1", idempotency_key="key-1")

    assert result["outcome"] == "in_progress"
    assert result["idempotent"] is True
    assert result["reservation"]["reservation_id"] == "reservation-1"
    assert remediation.apply_calls == 0
    assert authorization.issue_calls == 0
    assert service.evaluate_calls == 0


@pytest.mark.parametrize(
    "plan_updates",
    [
        {"plan_id": "different-plan"},
        {"plan_fingerprint": "different-fingerprint"},
        {"server_id": 9},
        {"proposed_actions": [{"id": "start-nginx", "action_type": "stop_service", "target": "nginx"}]},
        {"proposed_actions": [{"id": "start-nginx", "action_type": "start_service", "target": "other.service"}]},
    ],
)
def test_idempotency_binding_collision_fails_closed(plan_updates):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_idempotency_binding_collision_fails_closed؛ المدخلات المهمة: plan_updates.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, reservations, remediation, authorization, _ = make_service()
    original = service.attempt(plan_id="plan-1", idempotency_key="key-1")
    assert original["result"]["applied"] is True
    service._remediation_repository.plan = make_plan(**plan_updates)

    result = service.attempt(plan_id=service._remediation_repository.plan.plan_id, idempotency_key="key-1")

    assert result["outcome"] == "deny"
    assert result["error"] == "idempotency_reservation_binding_mismatch"
    assert result.get("idempotent") is not True
    assert remediation.apply_calls == 1
    assert authorization.issue_calls == 1
    assert len(reservations.reservations) == 1


def test_concurrent_attempts_share_one_atomic_reservation_and_execution():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_concurrent_attempts_share_one_atomic_reservation_and_execution؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, reservations, remediation, authorization, _ = make_service()
    results = []

    def run():
        """
        يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        results.append(service.attempt(plan_id="plan-1", idempotency_key="key-1"))

    threads = [Thread(target=run) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(reservations.reservations) == 1
    assert remediation.apply_calls == 1
    assert authorization.issue_calls == 1
    assert sum(result.get("idempotent") is True for result in results) >= 1
