"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.remediation.autonomous_execution_service، app.core.contracts.autonomous_remediation، app.core.contracts.remediation، app.core.policies.autonomous_remediation، app.interfaces.mcp.registry.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.capabilities.remediation.autonomous_execution_service import (
    AutonomousExecutionService,
)
from app.core.contracts.autonomous_remediation import (
    AutonomousDecisionOutcome,
    AutonomousEvaluationContext,
    AutonomousHistorySnapshot,
    AutonomousPolicyStatus,
    AutonomousRemediationPolicy,
)
from app.core.contracts.remediation import RemediationPlanStatus
from app.core.policies.autonomous_remediation import (
    AutonomousRemediationPolicyEvaluator,
)
from app.interfaces.mcp.registry import ProjectMcpToolBoundary


NOW = datetime(2026, 8, 14, tzinfo=timezone.utc)


def policy(**updates):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى policy؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    values = {
        "policy_id": "policy-1",
        "name": "Start nginx",
        "description": "negative security fixture",
        "status": AutonomousPolicyStatus.ENABLED,
        "version": 1,
        "issue_fingerprint": "issue-1",
        "allowed_action_type": "start_service",
        "allowed_target_pattern": "nginx",
        "minimum_success_count": 1,
        "maximum_failure_rate": 0.0,
        "maximum_rollback_failure_rate": 0.0,
        "allowed_server_ids": (4,),
    }
    values.update(updates)
    return AutonomousRemediationPolicy(**values)


def sandbox(**updates):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى sandbox؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    values = {
        "validation_id": "sandbox-1",
        "status": "passed",
        "plan_id": "plan-1",
        "plan_fingerprint": "plan-fp-1",
        "server_id": 4,
        "service": "nginx",
        "action_type": "start_service",
        "before_evidence_ids": ["before"],
        "after_evidence_ids": ["after"],
        "verification_status": "verified",
        "created_at": NOW,
    }
    values.update(updates)
    return SimpleNamespace(**values)


def history(**updates):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى history؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    values = {
        "issue_fingerprint": "issue-1",
        "action_type": "start_service",
        "target": "nginx",
        "supervised_execution_count": 1,
        "successful_execution_count": 1,
        "verified_success_count": 1,
    }
    values.update(updates)
    return AutonomousHistorySnapshot(**values)


def context(**updates):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى context؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    values = {
        "global_enabled": True,
        "now": NOW,
        "policy": policy(),
        "plan_id": "plan-1",
        "plan_fingerprint": "plan-fp-1",
        "issue_fingerprint": "issue-1",
        "server_id": 4,
        "action_type": "start_service",
        "target": "nginx",
        "risk": "low",
        "confidence": 0.95,
        "diagnosis_evidence_valid": True,
        "plan_evidence_valid": True,
        "sandbox": sandbox(),
        "sandbox_evidence_valid": True,
        "history": history(),
        "plan_ready": True,
    }
    values.update(updates)
    return AutonomousEvaluationContext(**values)


def evaluate(**updates):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى evaluate؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return AutonomousRemediationPolicyEvaluator().evaluate(context(**updates))


def assert_denied(result, reason: str | None = None):
    """
    يتحقق من invariant أو readiness شرطها ظاهر في الكود ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى assert_denied؛ المدخلات المهمة: result، reason.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    assert result.outcome is AutonomousDecisionOutcome.DENY
    if reason is not None:
        assert reason in result.reason_codes


@pytest.mark.parametrize(
    ("updates", "reason"),
    [
        ({"global_enabled": False}, "global_autonomy_disabled"),
        ({"policy": policy(status=AutonomousPolicyStatus.DISABLED)}, "policy_disabled"),
        ({"policy": policy(status=AutonomousPolicyStatus.SUSPENDED)}, "policy_suspended"),
        ({
            "policy": None,
            "ambiguous_policy_match": True,
        }, "ambiguous_policy_match"),
    ],
)
def test_global_and_policy_selection_gates_fail_closed(updates, reason):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_global_and_policy_selection_gates_fail_closed؛ المدخلات المهمة: updates، reason.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert_denied(evaluate(**updates), reason)


class SecurityRepository:
    """
    يمثل SecurityRepository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, policies):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: policies.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.policies = list(policies)
        self.decisions = []
        self.audit = []
        self.reserve_calls = 0

    def matching_policies(self, **_kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى matching_policies؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.policies

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
        return SimpleNamespace(policy_id=policy_id, consecutive_failures=0)

    def list_reservations(self, **_kwargs):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_reservations؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return []

    def create_decision(self, decision, **_kwargs):
        """
        يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى create_decision؛ المدخلات المهمة: decision.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.decisions.append(decision)

    def get_policy(self, policy_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_policy؛ المدخلات المهمة: policy_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return next((item for item in self.policies if item.policy_id == policy_id), None)

    def reserve(self, **_kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى reserve؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.reserve_calls += 1
        raise AssertionError("A negative decision must not create a reservation.")


class SecurityRemediationRepository:
    """
    يمثل SecurityRemediationRepository جزءًا من طبقة Test suite.

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
        self.sandbox = sandbox()

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
        return self.sandbox

    def sandbox_evidence_belongs(self, **_kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى sandbox_evidence_belongs؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return True


class SecurityRemediationService:
    """
    يمثل SecurityRemediationService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.apply_calls = 0
        self.approval_calls = 0

    def audit_autonomous(self, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى audit_autonomous؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.audit.append(kwargs)

    def request_approval(self, **_kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى request_approval؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.approval_calls += 1
        return SimpleNamespace()

    def apply_approved(self, **_kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى apply_approved؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.apply_calls += 1
        raise AssertionError("A negative decision must not execute remediation.")


class SecurityAuthorizationService:
    """
    يمثل SecurityAuthorizationService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.issue_calls = 0

    def issue(self, **_kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى issue؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.issue_calls += 1
        raise AssertionError("A negative decision must not issue authorization.")


def make_operational_service(*, policies, automatic_remediation_allowed=True):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_operational_service؛ المدخلات المهمة: policies، automatic_remediation_allowed.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    plan = SimpleNamespace(
        plan_id="plan-1",
        plan_fingerprint="plan-fp-1",
        server_id=4,
        status=RemediationPlanStatus.SANDBOX_PASSED.value,
        plan_metadata={"issue_fingerprint": "issue-1"},
        risk_level="low",
        diagnosis_claim_ids=["claim-1"],
        evidence_ids=["evidence-1"],
        proposed_actions=[{
            "id": "start-nginx",
            "action_type": "start_service",
            "target": "nginx",
        }],
    )
    repository = SecurityRepository(policies)
    remediation_repository = SecurityRemediationRepository(plan)
    remediation_service = SecurityRemediationService()
    authorization_service = SecurityAuthorizationService()
    remediation_service.audit = repository.audit
    service = AutonomousExecutionService(
        repository=repository,
        remediation_repository=remediation_repository,
        remediation_service=remediation_service,
        policy_service=SimpleNamespace(_model_to_contract=lambda model: model),
        history_service=SimpleNamespace(snapshot=lambda **kwargs: history(**kwargs)),
        candidate_service=SimpleNamespace(),
        authorization_service=authorization_service,
        automatic_remediation_allowed=automatic_remediation_allowed,
    )
    return service, repository, remediation_service, authorization_service


@pytest.mark.parametrize(
    ("policies", "automatic", "reason"),
    [
        ([policy()], False, "global_autonomy_disabled"),
        ([policy(status=AutonomousPolicyStatus.DISABLED)], True, "policy_disabled"),
        ([policy(status=AutonomousPolicyStatus.SUSPENDED)], True, "policy_suspended"),
        ([policy(), policy(policy_id="policy-2")], True, "ambiguous_policy_match"),
    ],
)
def test_service_negative_gates_create_no_execution_side_effects(policies, automatic, reason):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_service_negative_gates_create_no_execution_side_effects؛ المدخلات المهمة: policies، automatic، reason.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, repository, remediation, authorization = make_operational_service(
        policies=policies,
        automatic_remediation_allowed=automatic,
    )

    result = service.attempt(plan_id="plan-1")

    assert result["outcome"] == "deny"
    assert reason in result["decision"].reason_codes
    assert repository.reserve_calls == 0
    assert authorization.issue_calls == 0
    assert remediation.apply_calls == 0


def test_denial_is_persisted_and_audited():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_denial_is_persisted_and_audited؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service, repository, _remediation, _authorization = make_operational_service(
        policies=[policy()], automatic_remediation_allowed=False,
    )

    decision, *_ = service.evaluate(plan_id="plan-1")

    assert decision.outcome is AutonomousDecisionOutcome.DENY
    assert repository.decisions[0].decision_id == decision.decision_id
    assert repository.audit[0]["event_type"] == "autonomous_policy_evaluated"
    assert repository.audit[0]["payload"]["reason_codes"] == ["global_autonomy_disabled"]


def test_missing_fingerprint_requires_human_approval_and_never_uses_plan_fingerprint():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_missing_fingerprint_requires_human_approval_and_never_uses_plan_fingerprint؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = evaluate(issue_fingerprint="", plan_fingerprint="trusted-looking-plan-fp")

    assert result.outcome is AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL
    assert result.reason_codes == ("issue_fingerprint_missing",)


def test_issue_fingerprint_mismatch_cannot_auto_execute():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_issue_fingerprint_mismatch_cannot_auto_execute؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = evaluate(
        issue_fingerprint="issue-2",
        policy=policy(issue_fingerprint="issue-1"),
    )

    assert result.outcome is not AutonomousDecisionOutcome.AUTO_EXECUTE


@pytest.mark.parametrize(
    ("updates", "reason"),
    [
        ({"server_id": 9}, "server_not_allowed"),
        ({"target": "redis"}, "target_not_allowed"),
            ({"action_type": "stop_service"}, "hard_deny"),
    ],
)
def test_policy_scope_mismatches_fail_closed(updates, reason):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_policy_scope_mismatches_fail_closed؛ المدخلات المهمة: updates، reason.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert_denied(evaluate(**updates), reason)


@pytest.mark.parametrize(
    "action_type",
    [
        "stop_service", "reboot", "firewall_change", "package_install",
        "filesystem_repair", "restart_database", "arbitrary_shell", "raw_ssh", "raw_sql",
    ],
)
def test_hard_v1_allowlist_rejects_dangerous_actions(action_type):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_hard_v1_allowlist_rejects_dangerous_actions؛ المدخلات المهمة: action_type.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = evaluate(
        action_type=action_type,
        policy=policy(allowed_action_type=action_type),
    )
    assert_denied(result, "hard_deny")


@pytest.mark.parametrize("risk", ["medium", "high", "critical"])
def test_risk_ceiling_rejects_non_low_risk(risk):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_risk_ceiling_rejects_non_low_risk؛ المدخلات المهمة: risk.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert_denied(evaluate(risk=risk), "risk_too_high")


@pytest.mark.parametrize(
    ("updates", "reason"),
    [
        ({"sandbox": None}, "sandbox_missing"),
        ({"sandbox": sandbox(status="failed")}, "sandbox_failed"),
        ({"sandbox": sandbox(created_at=NOW - timedelta(hours=2)), "policy": policy(sandbox_max_age_seconds=60)}, "sandbox_stale"),
        ({"sandbox": sandbox(plan_fingerprint="other")}, "sandbox_fingerprint_mismatch"),
        ({"sandbox": sandbox(plan_id="other")}, "sandbox_fingerprint_mismatch"),
        ({"sandbox": sandbox(server_id=9)}, "target_not_allowed"),
        ({"sandbox": sandbox(action_type="stop_service")}, "target_not_allowed"),
        ({"sandbox": sandbox(service="redis")}, "target_not_allowed"),
        ({"sandbox": sandbox(before_evidence_ids=[])}, "evidence_incomplete"),
        ({"sandbox": sandbox(after_evidence_ids=[])}, "evidence_incomplete"),
        ({"sandbox": sandbox(verification_status="failed")}, "evidence_incomplete"),
        ({"sandbox_evidence_valid": False}, "evidence_incomplete"),
    ],
)
def test_sandbox_required_fresh_and_bound(updates, reason):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_sandbox_required_fresh_and_bound؛ المدخلات المهمة: updates، reason.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert_denied(evaluate(**updates), reason)


@pytest.mark.parametrize(
    "updates",
    [
        {"diagnosis_evidence_valid": False},
        {"plan_evidence_valid": False},
    ],
)
def test_diagnosis_and_plan_evidence_are_required(updates):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_diagnosis_and_plan_evidence_are_required؛ المدخلات المهمة: updates.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert_denied(evaluate(**updates), "evidence_incomplete")


def test_rollback_capability_is_required():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_rollback_capability_is_required؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert_denied(evaluate(policy=policy(rollback_required=False)), "rollback_unavailable")


def test_insufficient_history_falls_back_to_human_approval():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_insufficient_history_falls_back_to_human_approval؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = evaluate(history=history(verified_success_count=0, supervised_execution_count=0))
    assert result.outcome is AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL
    assert "historical_successes_insufficient" in result.reason_codes


@pytest.mark.parametrize(
    "updates",
    [
        {"history": history(failed_execution_count=1, supervised_execution_count=2)},
        {"history": history(rollback_required_count=2, rollback_failure_count=1)},
    ],
)
def test_history_failure_ceilings_deny(updates):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_history_failure_ceilings_deny؛ المدخلات المهمة: updates.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert_denied(evaluate(**updates), "historical_failure_rate_too_high")


@pytest.mark.parametrize(
    "updates",
    [
        {"hourly_execution_count": 1},
        {"daily_execution_count": 3},
        {"last_execution_at": NOW - timedelta(seconds=1), "policy": policy(cooldown_seconds=60)},
        {"consecutive_failures": 1},
    ],
)
def test_runtime_limits_deny_without_a_new_execution(updates):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_limits_deny_without_a_new_execution؛ المدخلات المهمة: updates.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = evaluate(**updates)
    assert_denied(result)
    assert result.outcome is not AutonomousDecisionOutcome.AUTO_EXECUTE


def test_authorization_binding_rejects_every_immutable_field_change():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_authorization_binding_rejects_every_immutable_field_change؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    from tests.test_autonomous_execution_idempotency import make_service

    immutable_fields = {
        "policy_id": "other-policy",
        "policy_version": 2,
        "decision_id": "other-decision",
        "plan_id": "other-plan",
        "plan_fingerprint": "other-fingerprint",
        "server_id": 9,
        "action_type": "stop_service",
        "target": "redis",
        "sandbox_validation_id": "other-sandbox",
    }
    for field, value in immutable_fields.items():
        service, _reservations, remediation, authorization, _repository = make_service()
        original_consume = authorization.consume

        def consume(authorization_id, *, _original=original_consume, _field=field, _value=value):
            """
            ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

            تُستدعى عندما يصل المسار إلى consume؛ المدخلات المهمة: authorization_id، _original، _field، _value.
            تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
            """
            issued = _original(authorization_id)
            setattr(issued, _field, _value)
            return issued

        authorization.consume = consume
        result = service.attempt(plan_id="plan-1", idempotency_key=f"binding-{field}")

        assert result["outcome"] == "deny", field
        assert result["error"] == "authorization_stale:binding", field
        assert remediation.apply_calls == 0, field


def test_claude_mcp_surface_cannot_bypass_phase7_safety_gates():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_claude_mcp_surface_cannot_bypass_phase7_safety_gates؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    boundary = ProjectMcpToolBoundary(
        server_service=None,
        monitoring_profile_service=None,
        monitoring_service=None,
        report_query_service=None,
    )
    definitions = {item.tool_id: item for item in boundary.list_tools()}
    autonomous = definitions["attempt_autonomous_remediation"]

    assert autonomous.input_schema == {
        "type": "object",
        "properties": {"plan_id": {"type": "string"}},
        "required": ["plan_id"],
        "additionalProperties": False,
    }
    serialized = json.dumps(
        [
            {
                "tool_id": item.tool_id,
                "description": item.description,
                "input_schema": item.input_schema,
            }
            for item in definitions.values()
        ],
        sort_keys=True,
    ).lower()
    for forbidden in (
        "enable_policy", "resume_policy", "force_execute", "raw_ssh", "raw_sql",
        "unrestricted_shell", "arbitrary_command", "automatic_remediation_allowed",
    ):
        assert forbidden not in serialized

    assert not {
        "enable_autonomy", "create_policy", "enable_policy", "resume_policy",
        "force_execution", "raw_ssh", "raw_sql", "unrestricted_shell",
    } & definitions.keys()


def test_mcp_autonomous_attempt_only_forwards_bounded_plan_identity():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_mcp_autonomous_attempt_only_forwards_bounded_plan_identity؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    calls = []

    class AutonomousSpy:
        """
        يمثل AutonomousSpy جزءًا من طبقة Test suite.

        يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
        تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
        """
        def attempt(self, **kwargs):
            """
            ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

            تُستدعى عندما يصل المسار إلى attempt؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
            تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
            """
            calls.append(kwargs)
            return {"outcome": "deny"}

    boundary = ProjectMcpToolBoundary(
        server_service=None,
        monitoring_profile_service=None,
        monitoring_service=None,
        report_query_service=None,
        autonomous_execution_service=AutonomousSpy(),
    )
    result = asyncio.run(boundary.execute(SimpleNamespace(
        tool_id="attempt_autonomous_remediation",
        arguments={
            "plan_id": "plan-1",
            "raw_ssh": "rm -rf /",
            "raw_sql": "DROP TABLE secrets",
        },
    )))

    assert result.success is False
    assert calls == [{"plan_id": "plan-1", "actor": "claude-autonomous-policy"}]
