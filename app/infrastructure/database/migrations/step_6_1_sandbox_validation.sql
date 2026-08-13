-- Phase 6 is additive. Native sandbox validation is persisted separately from
-- the Phase 5 legacy dry-run result and binds to the exact plan fingerprint.
CREATE TABLE IF NOT EXISTS sandbox_validations (
    id BIGSERIAL PRIMARY KEY,
    validation_id VARCHAR(64) NOT NULL UNIQUE,
    plan_id VARCHAR(64) NOT NULL,
    plan_fingerprint VARCHAR(64) NOT NULL,
    server_id INTEGER NOT NULL REFERENCES servers(id) ON DELETE RESTRICT,
    server_name VARCHAR(100) NOT NULL,
    service VARCHAR(128) NOT NULL,
    action_type VARCHAR(80) NOT NULL,
    action_parameters JSON NOT NULL DEFAULT '{}'::json,
    expected_state VARCHAR(30) NOT NULL,
    observed_state VARCHAR(30),
    before_evidence_ids JSON NOT NULL DEFAULT '[]'::json,
    after_evidence_ids JSON NOT NULL DEFAULT '[]'::json,
    verification_status VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    failure_reason VARCHAR(4000),
    metadata JSON NOT NULL DEFAULT '{}'::json,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_sandbox_validations_plan_created
    ON sandbox_validations (plan_id, created_at);
CREATE INDEX IF NOT EXISTS ix_sandbox_validations_plan_fingerprint
    ON sandbox_validations (plan_id, plan_fingerprint);
CREATE INDEX IF NOT EXISTS ix_sandbox_validations_status
    ON sandbox_validations (status);
