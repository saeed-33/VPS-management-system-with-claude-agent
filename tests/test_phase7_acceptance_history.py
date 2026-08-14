from types import SimpleNamespace

from tests.real_runtime.test_phase7_real_autonomous_acceptance import (
    _assert_candidate_delta,
    _assert_history_delta,
)


def test_acceptance_history_delta_requires_three_new_clean_successes():
    baseline = SimpleNamespace(
        supervised_execution_count=3,
        successful_execution_count=3,
        verified_success_count=3,
        failed_execution_count=1,
        verification_failure_count=0,
        rollback_failure_count=0,
    )
    current = SimpleNamespace(
        supervised_execution_count=6,
        successful_execution_count=6,
        verified_success_count=6,
        failed_execution_count=1,
        verification_failure_count=0,
        rollback_failure_count=0,
    )

    _assert_history_delta(baseline, current)


def test_acceptance_candidate_delta_allows_legitimate_prior_history():
    baseline = SimpleNamespace(
        execution_count=3,
        verified_success_count=3,
        failure_count=0,
        rollback_failure_count=0,
    )
    current = SimpleNamespace(
        execution_count=6,
        verified_success_count=6,
        failure_count=0,
        rollback_failure_count=0,
        success_rate=1.0,
    )

    _assert_candidate_delta(baseline, current)
