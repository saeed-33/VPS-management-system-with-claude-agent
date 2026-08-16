"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.contracts.autonomous_remediation، app.core.policies.autonomous_remediation، app.capabilities.remediation.autonomous_execution_service.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.core.contracts.autonomous_remediation import (
    AutonomousDecisionOutcome,
    AutonomousEvaluationContext,
    AutonomousHistorySnapshot,
    AutonomousPolicyStatus,
    AutonomousRemediationPolicy,
)
from app.core.policies.autonomous_remediation import AutonomousRemediationPolicyEvaluator
from app.capabilities.remediation.autonomous_execution_service import AutonomousExecutionService


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
        "description": "safe lab policy",
        "status": AutonomousPolicyStatus.ENABLED,
        "version": 1,
        "issue_fingerprint": "issue-1",
        "allowed_action_type": "start_service",
        "allowed_target_pattern": "nginx",
        "minimum_success_count": 1,
        "maximum_failure_rate": 0.0,
        "allowed_server_ids": (4,),
    }
    values.update(updates)
    return AutonomousRemediationPolicy(**values)


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
        "plan_fingerprint": "fp-1",
        "issue_fingerprint": "issue-1",
        "server_id": 4,
        "action_type": "start_service",
        "target": "nginx",
        "risk": "low",
        "confidence": 0.95,
        "diagnosis_evidence_valid": True,
        "plan_evidence_valid": True,
        "sandbox": SimpleNamespace(
            status="passed", plan_id="plan-1", plan_fingerprint="fp-1",
            server_id=4, service="nginx", action_type="start_service",
            before_evidence_ids=["before"], after_evidence_ids=["after"],
            verification_status="verified", created_at=NOW,
        ),
        "sandbox_evidence_valid": True,
        "history": AutonomousHistorySnapshot(
            issue_fingerprint="issue-1", action_type="start_service", target="nginx",
            supervised_execution_count=1, successful_execution_count=1,
            verified_success_count=1,
        ),
        "plan_ready": True,
    }
    values.update(updates)
    return AutonomousEvaluationContext(**values)


def test_valid_low_risk_context_auto_executes():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_valid_low_risk_context_auto_executes؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = AutonomousRemediationPolicyEvaluator().evaluate(context())
    assert result.outcome is AutonomousDecisionOutcome.AUTO_EXECUTE
    assert "policy_match" in result.reason_codes


def test_global_kill_switch_denies_even_with_valid_policy():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_global_kill_switch_denies_even_with_valid_policy؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = AutonomousRemediationPolicyEvaluator().evaluate(context(global_enabled=False))
    assert result.outcome is AutonomousDecisionOutcome.DENY
    assert result.reason_codes == ("global_autonomy_disabled",)


def test_missing_issue_fingerprint_requires_human_approval():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_missing_issue_fingerprint_requires_human_approval؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = AutonomousRemediationPolicyEvaluator().evaluate(context(issue_fingerprint=""))
    assert result.outcome is AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL
    assert "issue_fingerprint_missing" in result.reason_codes


@pytest.mark.parametrize("action", ["stop_service", "restart_service", "reload_service", "reboot", "raw_command"])
def test_v1_hard_allowlist_denies_other_actions(action):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_v1_hard_allowlist_denies_other_actions؛ المدخلات المهمة: action.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = AutonomousRemediationPolicyEvaluator().evaluate(
        context(action_type=action, policy=policy(allowed_action_type=action))
    )
    assert result.outcome is AutonomousDecisionOutcome.DENY
    assert "hard_deny" in result.reason_codes


def test_missing_policy_requires_human_approval():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_missing_policy_requires_human_approval؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = AutonomousRemediationPolicyEvaluator().evaluate(context(policy=None))
    assert result.outcome is AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL
    assert result.reason_codes == ("no_policy_match",)


def test_non_ready_plan_cannot_auto_execute_even_with_passed_sandbox():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_non_ready_plan_cannot_auto_execute_even_with_passed_sandbox؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = AutonomousRemediationPolicyEvaluator().evaluate(context(plan_ready=False))
    assert result.outcome is AutonomousDecisionOutcome.DENY
    assert "hard_deny" in result.reason_codes


def test_ambiguous_policy_match_denies():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_ambiguous_policy_match_denies؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = AutonomousRemediationPolicyEvaluator().evaluate(context(policy=None, ambiguous_policy_match=True))
    assert result.outcome is AutonomousDecisionOutcome.DENY
    assert result.reason_codes == ("ambiguous_policy_match",)


@pytest.mark.parametrize(
    ("statuses", "selected_status", "ambiguous"),
    [
        ((AutonomousPolicyStatus.ENABLED,), AutonomousPolicyStatus.ENABLED, False),
        ((AutonomousPolicyStatus.ENABLED, AutonomousPolicyStatus.DISABLED), AutonomousPolicyStatus.ENABLED, False),
        ((AutonomousPolicyStatus.ENABLED, AutonomousPolicyStatus.SUSPENDED), AutonomousPolicyStatus.ENABLED, False),
        ((AutonomousPolicyStatus.ENABLED, AutonomousPolicyStatus.ENABLED), None, True),
        ((AutonomousPolicyStatus.DISABLED,), AutonomousPolicyStatus.DISABLED, False),
        ((AutonomousPolicyStatus.SUSPENDED,), AutonomousPolicyStatus.SUSPENDED, False),
        ((), None, False),
    ],
)
def test_policy_selection_is_status_aware(statuses, selected_status, ambiguous):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_policy_selection_is_status_aware؛ المدخلات المهمة: statuses، selected_status، ambiguous.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    matches = [SimpleNamespace(status=status) for status in statuses]

    selected, actual_ambiguous = AutonomousExecutionService._select_policy(matches)

    assert actual_ambiguous is ambiguous
    assert (selected.status if selected is not None else None) == selected_status


def test_enabled_policy_precedence_allows_evaluation_with_inactive_history():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_enabled_policy_precedence_allows_evaluation_with_inactive_history؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    selected, ambiguous = AutonomousExecutionService._select_policy([
        SimpleNamespace(status=AutonomousPolicyStatus.ENABLED),
        SimpleNamespace(status=AutonomousPolicyStatus.DISABLED),
    ])

    result = AutonomousRemediationPolicyEvaluator().evaluate(
        context(ambiguous_policy_match=ambiguous)
    )

    assert selected.status is AutonomousPolicyStatus.ENABLED
    assert result.outcome is AutonomousDecisionOutcome.AUTO_EXECUTE


def test_multiple_enabled_policies_fail_closed_in_evaluator():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_multiple_enabled_policies_fail_closed_in_evaluator؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    selected, ambiguous = AutonomousExecutionService._select_policy([
        SimpleNamespace(status=AutonomousPolicyStatus.ENABLED),
        SimpleNamespace(status=AutonomousPolicyStatus.ENABLED),
    ])

    result = AutonomousRemediationPolicyEvaluator().evaluate(
        context(policy=None, ambiguous_policy_match=ambiguous)
    )

    assert selected is None
    assert result.outcome is AutonomousDecisionOutcome.DENY
    assert result.reason_codes == ("ambiguous_policy_match",)


def test_single_inactive_policy_preserves_explicit_deny_semantics():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_single_inactive_policy_preserves_explicit_deny_semantics؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    for status, reason in (
        (AutonomousPolicyStatus.DISABLED, "policy_disabled"),
        (AutonomousPolicyStatus.SUSPENDED, "policy_suspended"),
    ):
        selected, ambiguous = AutonomousExecutionService._select_policy([
            SimpleNamespace(status=status),
        ])
        result = AutonomousRemediationPolicyEvaluator().evaluate(
            context(policy=policy(status=status), ambiguous_policy_match=ambiguous)
        )
        assert selected.status is status
        assert result.outcome is AutonomousDecisionOutcome.DENY
        assert result.reason_codes == (reason,)


def test_sandbox_mismatch_and_stale_are_denied():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_sandbox_mismatch_and_stale_are_denied؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    mismatch = AutonomousRemediationPolicyEvaluator().evaluate(
        context(sandbox=SimpleNamespace(
            status="passed", plan_id="plan-2", plan_fingerprint="fp-2", server_id=4,
            service="nginx", action_type="start_service", before_evidence_ids=["b"],
            after_evidence_ids=["a"], verification_status="verified", created_at=NOW,
        ))
    )
    assert "sandbox_fingerprint_mismatch" in mismatch.reason_codes

    stale = AutonomousRemediationPolicyEvaluator().evaluate(
        context(sandbox=SimpleNamespace(
            status="passed", plan_id="plan-1", plan_fingerprint="fp-1", server_id=4,
            service="nginx", action_type="start_service", before_evidence_ids=["b"],
            after_evidence_ids=["a"], verification_status="verified",
            created_at=NOW - timedelta(hours=2),
        ), policy=policy(sandbox_max_age_seconds=60))
    )
    assert "sandbox_stale" in stale.reason_codes


def test_insufficient_history_requires_human_approval():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_insufficient_history_requires_human_approval؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = AutonomousRemediationPolicyEvaluator().evaluate(
        context(history=AutonomousHistorySnapshot(
            issue_fingerprint="issue-1", action_type="start_service", target="nginx",
        ))
    )
    assert result.outcome is AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL
    assert "historical_successes_insufficient" in result.reason_codes
