-- Phase 7 is additive. It never rewrites or deletes Phase 5/6 records.
CREATE TABLE IF NOT EXISTS autonomous_remediation_policies (
    id BIGSERIAL PRIMARY KEY,
    policy_id VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    description VARCHAR(4000) NOT NULL DEFAULT '',
    status VARCHAR(30) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    issue_fingerprint VARCHAR(128) NOT NULL,
    allowed_action_type VARCHAR(80) NOT NULL,
    allowed_target_pattern VARCHAR(128) NOT NULL,
    maximum_risk VARCHAR(20) NOT NULL DEFAULT 'low',
    minimum_confidence DOUBLE PRECISION NOT NULL DEFAULT 0,
    required_evidence JSON NOT NULL DEFAULT '[]',
    minimum_success_count INTEGER NOT NULL DEFAULT 0,
    maximum_failure_rate DOUBLE PRECISION NOT NULL DEFAULT 0,
    maximum_rollback_failure_rate DOUBLE PRECISION NOT NULL DEFAULT 0,
    allowed_server_ids JSON NOT NULL DEFAULT '[]',
    allowed_server_tags JSON NOT NULL DEFAULT '[]',
    sandbox_required BOOLEAN NOT NULL DEFAULT TRUE,
    sandbox_max_age_seconds INTEGER NOT NULL DEFAULT 3600,
    rollback_required BOOLEAN NOT NULL DEFAULT TRUE,
    cooldown_seconds INTEGER NOT NULL DEFAULT 0,
    max_executions_per_hour INTEGER NOT NULL DEFAULT 1,
    max_executions_per_day INTEGER NOT NULL DEFAULT 3,
    max_consecutive_failures INTEGER NOT NULL DEFAULT 1,
    auto_suspend_on_failure BOOLEAN NOT NULL DEFAULT TRUE,
    created_by VARCHAR(120) NOT NULL,
    updated_by VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_autonomous_policies_match ON autonomous_remediation_policies(issue_fingerprint, allowed_action_type, status);

CREATE TABLE IF NOT EXISTS autonomous_policy_decisions (
    id BIGSERIAL PRIMARY KEY,
    decision_id VARCHAR(64) NOT NULL UNIQUE,
    policy_id VARCHAR(64), policy_version INTEGER,
    plan_id VARCHAR(64) NOT NULL, plan_fingerprint VARCHAR(64) NOT NULL,
    issue_fingerprint VARCHAR(128) NOT NULL, server_id INTEGER,
    action_type VARCHAR(80) NOT NULL, target VARCHAR(128) NOT NULL,
    outcome VARCHAR(40) NOT NULL, reason_codes JSON NOT NULL DEFAULT '[]',
    human_readable_reasons JSON NOT NULL DEFAULT '[]',
    history_snapshot JSON NOT NULL DEFAULT '{}', evaluation_metadata JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_autonomous_decisions_plan_created ON autonomous_policy_decisions(plan_id, created_at);
CREATE INDEX IF NOT EXISTS ix_autonomous_decisions_policy_created ON autonomous_policy_decisions(policy_id, created_at);

CREATE TABLE IF NOT EXISTS autonomous_authorizations (
    id BIGSERIAL PRIMARY KEY,
    authorization_id VARCHAR(64) NOT NULL UNIQUE,
    token VARCHAR(128) NOT NULL UNIQUE,
    status VARCHAR(30) NOT NULL,
    policy_id VARCHAR(64) NOT NULL, policy_version INTEGER NOT NULL,
    decision_id VARCHAR(64) NOT NULL, plan_id VARCHAR(64) NOT NULL,
    plan_fingerprint VARCHAR(64) NOT NULL, server_id INTEGER NOT NULL,
    action_type VARCHAR(80) NOT NULL, target VARCHAR(128) NOT NULL,
    sandbox_validation_id VARCHAR(64) NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL, expires_at TIMESTAMPTZ NOT NULL,
    consumed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_autonomous_authorizations_plan ON autonomous_authorizations(plan_id, status);

CREATE TABLE IF NOT EXISTS autonomous_policy_execution_reservations (
    id BIGSERIAL PRIMARY KEY,
    reservation_id VARCHAR(64) NOT NULL UNIQUE,
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    owner_token VARCHAR(128) NOT NULL,
    policy_id VARCHAR(64) NOT NULL, plan_id VARCHAR(64) NOT NULL,
    plan_fingerprint VARCHAR(64) NOT NULL, action_type VARCHAR(80) NOT NULL,
    target VARCHAR(128) NOT NULL, server_id INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL, authorization_id VARCHAR(64), execution_id VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), expires_at TIMESTAMPTZ, completed_at TIMESTAMPTZ
);
ALTER TABLE autonomous_policy_execution_reservations ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ;
ALTER TABLE autonomous_policy_execution_reservations ADD COLUMN IF NOT EXISTS owner_token VARCHAR(128);
UPDATE autonomous_policy_execution_reservations SET owner_token = reservation_id WHERE owner_token IS NULL;
ALTER TABLE autonomous_policy_execution_reservations ALTER COLUMN owner_token SET NOT NULL;
CREATE INDEX IF NOT EXISTS ix_autonomous_reservations_plan ON autonomous_policy_execution_reservations(plan_id, created_at);
CREATE INDEX IF NOT EXISTS ix_autonomous_reservations_expires ON autonomous_policy_execution_reservations(expires_at);
CREATE INDEX IF NOT EXISTS ix_autonomous_reservations_owner ON autonomous_policy_execution_reservations(owner_token);

CREATE TABLE IF NOT EXISTS autonomous_policy_runtime_state (
    id BIGSERIAL PRIMARY KEY,
    policy_id VARCHAR(64) NOT NULL UNIQUE,
    last_execution_at TIMESTAMPTZ, consecutive_failures INTEGER NOT NULL DEFAULT 0,
    suspended_at TIMESTAMPTZ, suspension_reason VARCHAR(80),
    triggering_execution_id VARCHAR(64), triggering_decision_id VARCHAR(64),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_autonomous_runtime_policy ON autonomous_policy_runtime_state(policy_id);

-- Policy-level events have no remediation plan foreign key. Execution events
-- remain in remediation_audit_events; these records cover operator actions
-- such as resume/enable and preserve the policy epoch independently.
CREATE TABLE IF NOT EXISTS autonomous_policy_audit_events (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL UNIQUE,
    policy_id VARCHAR(64) NOT NULL,
    policy_version INTEGER NOT NULL,
    event_type VARCHAR(80) NOT NULL,
    actor VARCHAR(120) NOT NULL DEFAULT 'admin',
    payload JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_autonomous_policy_audit_policy_created ON autonomous_policy_audit_events(policy_id, created_at);
CREATE INDEX IF NOT EXISTS ix_autonomous_policy_audit_event_type ON autonomous_policy_audit_events(event_type);
