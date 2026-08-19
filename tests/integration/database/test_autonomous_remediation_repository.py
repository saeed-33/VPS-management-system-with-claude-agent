"""Tests for test autonomous remediation repository.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.contracts.autonomous_remediation، app.infrastructure.database.base، app.infrastructure.database.models، app.infrastructure.database.models.remediation، app.infrastructure.database.repositories.autonomous_remediation_repository.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.contracts.autonomous_remediation.autonomous_policy_status import AutonomousPolicyStatus
from app.core.contracts.autonomous_remediation.autonomous_remediation_policy import AutonomousRemediationPolicy
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.remediation.autonomous_authorization import AutonomousAuthorizationModel
from app.infrastructure.database.models.remediation.autonomous_decision import AutonomousPolicyDecisionModel
from app.infrastructure.database.models.remediation.autonomous_reservation import AutonomousPolicyExecutionReservationModel
from app.infrastructure.database.models.remediation.autonomous_runtime import AutonomousPolicyRuntimeStateModel
from app.infrastructure.database.models.remediation.autonomous_policy import AutonomousRemediationPolicyModel
from app.infrastructure.database.models.remediation.evidence import RemediationEvidenceModel
from app.infrastructure.database.models.remediation.execution import RemediationExecutionModel
from app.infrastructure.database.models.remediation.plan import RemediationPlanModel
from app.infrastructure.database.models.remediation.rollback import RemediationRollbackModel
from app.infrastructure.database.models.remediation.verification import RemediationVerificationModel
from app.infrastructure.database.repositories.autonomous_remediation_repository.repository import AutonomousRemediationRepository


def repository():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى repository؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    for model in (
        RemediationPlanModel,
        RemediationExecutionModel,
        RemediationEvidenceModel,
        RemediationVerificationModel,
        RemediationRollbackModel,
        AutonomousRemediationPolicyModel,
        AutonomousPolicyDecisionModel,
        AutonomousAuthorizationModel,
        AutonomousPolicyExecutionReservationModel,
        AutonomousPolicyRuntimeStateModel,
    ):
        model.__table__.create(engine)
    return AutonomousRemediationRepository(sessionmaker(bind=engine, expire_on_commit=False))


def test_policy_version_updates_and_status_changes_are_persisted():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_policy_version_updates_and_status_changes_are_persisted؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repo = repository()
    policy = AutonomousRemediationPolicy(
        policy_id="p1", name="p1", description="test", status=AutonomousPolicyStatus.DISABLED,
        version=1, issue_fingerprint="fp", allowed_action_type="start_service", allowed_target_pattern="nginx",
    )
    repo.create_policy(policy)
    enabled = repo.update_policy("p1", updates={"status": "enabled", "name": "p1-updated"}, version=2)
    assert enabled.version == 2
    assert enabled.status == "enabled"
    assert enabled.name == "p1-updated"


def test_reservation_lookup_by_idempotency_key_preserves_persisted_binding():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_reservation_lookup_by_idempotency_key_preserves_persisted_binding؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repo = repository()
    now = datetime.now(timezone.utc)
    created = repo.reserve(
        idempotency_key="replay-key", owner_token="worker-1", policy_id="p1",
        plan_id="plan-1", plan_fingerprint="fingerprint-1", action_type="start_service",
        target="nginx", server_id=4, now=now,
    )

    found = repo.get_reservation_by_idempotency_key("replay-key")

    assert found.reservation_id == created.reservation_id
    assert found.plan_id == "plan-1"
    assert found.plan_fingerprint == "fingerprint-1"
    assert found.server_id == 4
    assert found.action_type == "start_service"
    assert found.target == "nginx"


def test_matching_policies_returns_structural_matches_across_statuses_and_scope():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_matching_policies_returns_structural_matches_across_statuses_and_scope؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repo = repository()

    def add(policy_id, *, status=AutonomousPolicyStatus.ENABLED, fingerprint="fp", target="nginx", servers=(4,)):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى add؛ المدخلات المهمة: policy_id، status، fingerprint، target، servers.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        repo.create_policy(AutonomousRemediationPolicy(
            policy_id=policy_id, name=policy_id, description="test", status=status,
            version=1, issue_fingerprint=fingerprint, allowed_action_type="start_service",
            allowed_target_pattern=target, allowed_server_ids=servers,
        ))

    add("enabled")
    add("disabled", status=AutonomousPolicyStatus.DISABLED)
    add("suspended", status=AutonomousPolicyStatus.SUSPENDED)
    add("other-fingerprint", fingerprint="other")
    add("other-target", target="other.service")
    add("other-server", servers=(9,))

    matches = repo.matching_policies(
        issue_fingerprint="fp", action_type="start_service", target="nginx", server_id=4,
    )

    assert {item.policy_id for item in matches} == {"enabled", "disabled", "suspended"}
    assert repo.get_policy("disabled").status == AutonomousPolicyStatus.DISABLED.value
    assert repo.get_policy("suspended").status == AutonomousPolicyStatus.SUSPENDED.value


def test_reservation_idempotency_and_single_use_authorization():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_reservation_idempotency_and_single_use_authorization؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    from datetime import datetime, timezone, timedelta
    from app.core.contracts.autonomous_remediation.autonomous_authorization import AutonomousAuthorization
    from app.core.contracts.autonomous_remediation.autonomous_authorization_status import AutonomousAuthorizationStatus

    repo = repository()
    now = datetime.now(timezone.utc)
    first = repo.reserve(idempotency_key="k1", owner_token="worker-1", policy_id="p1", plan_id="plan", plan_fingerprint="fp", action_type="start_service", target="nginx", server_id=4, now=now)
    second = repo.reserve(idempotency_key="k1", owner_token="worker-1", policy_id="p1", plan_id="plan", plan_fingerprint="fp", action_type="start_service", target="nginx", server_id=4, now=now)
    assert first.reservation_id == second.reservation_id

    competing = repo.reserve(idempotency_key="k2", owner_token="worker-2", policy_id="p1", plan_id="plan", plan_fingerprint="fp", action_type="start_service", target="nginx", server_id=4, now=now)
    assert competing.status == "in_progress"

    recovered = repo.reserve(idempotency_key="k3", owner_token="worker-1", policy_id="p1", plan_id="plan-2", plan_fingerprint="fp", action_type="start_service", target="nginx", server_id=4, now=now, lease_seconds=1)
    recovered_again = repo.reserve(idempotency_key="k3", owner_token="worker-2", policy_id="p1", plan_id="plan-2", plan_fingerprint="fp", action_type="start_service", target="nginx", server_id=4, now=now + timedelta(seconds=2))
    assert recovered_again.status == "reserved"
    assert recovered_again.owner_token == "worker-2"

    auth = AutonomousAuthorization(
        authorization_id="a1", token="token1", status=AutonomousAuthorizationStatus.VALID,
        policy_id="p1", policy_version=1, decision_id="d1", plan_id="plan", plan_fingerprint="fp",
        server_id=4, action_type="start_service", target="nginx", sandbox_validation_id="sv1",
        issued_at=now, expires_at=now + timedelta(minutes=5),
    )
    repo.create_authorization(auth)
    repo.consume_authorization("a1", now=now)
    try:
        repo.consume_authorization("a1", now=now)
    except ValueError as exc:
        assert "not valid" in str(exc)
    else:
        raise AssertionError("Consumed authorization was reusable.")


def test_history_and_candidates_group_trusted_issue_across_distinct_plans():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_history_and_candidates_group_trusted_issue_across_distinct_plans؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    from datetime import datetime, timezone
    from app.capabilities.remediation.autonomous_candidate_service import AutonomousCandidateService
    from app.infrastructure.database.models.remediation.execution import RemediationExecutionModel
    from app.infrastructure.database.models.remediation.plan import RemediationPlanModel
    from app.infrastructure.database.models.remediation.verification import RemediationVerificationModel

    repo = repository()
    now = datetime.now(timezone.utc)
    with repo._session_factory() as session:
        for index in range(3):
            plan_id = f"trusted-plan-{index}"
            execution_id = f"trusted-execution-{index}"
            session.add(RemediationPlanModel(
                plan_id=plan_id, investigation_id=f"inv-{index}", server_id=4,
                title="Start service", problem_summary="service inactive",
                proposed_actions=[{"id": f"action-{index}", "action_type": "start_service", "target": "nginx"}],
                diagnosis_claim_ids=[f"claim-{index}"], evidence_ids=[f"evidence-{index}"],
                risk_level="low", plan_version=1, plan_fingerprint=f"plan-fp-{index}",
                status="succeeded", plan_metadata={"issue_fingerprint": "issue-stable"},
                created_at=now, updated_at=now,
            ))
            session.add(RemediationExecutionModel(
                execution_id=execution_id, plan_id=plan_id, action_id=f"action-{index}",
                server_id=4, status="succeeded", idempotency_key=f"key-{index}",
                before_evidence_ids=[], after_evidence_ids=[], stdout="", stderr="",
                execution_metadata={}, created_at=now, completed_at=now,
            ))
            session.add(RemediationVerificationModel(
                verification_id=f"verification-{index}", execution_id=execution_id,
                status="verified", before_evidence_ids=[], after_evidence_ids=[], details={}, created_at=now,
            ))
        session.add(RemediationPlanModel(
            plan_id="legacy-plan", investigation_id="legacy-inv", server_id=4,
            title="Legacy", problem_summary="legacy", proposed_actions=[{"id": "legacy-action", "action_type": "start_service", "target": "nginx"}],
            diagnosis_claim_ids=["legacy-claim"], evidence_ids=["legacy-evidence"], risk_level="low",
            plan_version=1, plan_fingerprint="legacy-plan-fingerprint", status="succeeded", plan_metadata={},
            created_at=now, updated_at=now,
        ))
        session.commit()

    history = repo.history(issue_fingerprint="issue-stable", action_type="start_service", target="nginx")
    assert history.supervised_execution_count == 3
    assert history.successful_execution_count == 3
    assert history.verified_success_count == 3
    assert history.failed_execution_count == 0
    assert history.rollback_failure_count == 0

    candidates = repo.candidate_keys()
    assert list(candidates) == [("issue-stable", "start_service", "nginx")]
    assert len(candidates[("issue-stable", "start_service", "nginx")]["executions"]) == 3

    policy_candidates = AutonomousCandidateService(repository=repo).list_candidates()
    assert len(policy_candidates) == 1
    assert policy_candidates[0].issue_fingerprint == "issue-stable"
    assert policy_candidates[0].execution_count == 3
    assert policy_candidates[0].success_rate == 1.0
    assert policy_candidates[0].reason_codes == ("eligible_for_policy_review",)
