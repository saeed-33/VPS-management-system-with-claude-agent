-- Keep one policy for each identical problem/action/target/scope definition.
-- Runtime rows are removed first because they belong to discarded policy IDs.

BEGIN;

CREATE TEMP TABLE duplicate_policy_ids ON COMMIT DROP AS
SELECT policy_id
FROM (
    SELECT
        policy_id,
        ROW_NUMBER() OVER (
            PARTITION BY
                name,
                description,
                issue_fingerprint,
                allowed_action_type,
                allowed_target_pattern,
                maximum_risk,
                minimum_confidence,
                required_evidence::text,
                minimum_success_count,
                maximum_failure_rate,
                maximum_rollback_failure_rate,
                allowed_server_ids::text,
                allowed_server_tags::text,
                sandbox_required,
                sandbox_max_age_seconds,
                rollback_required,
                cooldown_seconds,
                max_executions_per_hour,
                max_executions_per_day,
                max_consecutive_failures,
                auto_suspend_on_failure
            ORDER BY created_at, policy_id
        ) AS duplicate_rank
    FROM autonomous_remediation_policies
) ranked
WHERE duplicate_rank > 1;

DELETE FROM autonomous_policy_runtime_state
WHERE policy_id IN (SELECT policy_id FROM duplicate_policy_ids);

DELETE FROM autonomous_remediation_policies
WHERE policy_id IN (SELECT policy_id FROM duplicate_policy_ids);

COMMIT;
