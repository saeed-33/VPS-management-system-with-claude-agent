-- Phase 5 is additive. Existing remediation plans and sandbox results remain
-- valid and are never rewritten or deleted.
ALTER TABLE IF EXISTS remediation_plans
    ADD COLUMN IF NOT EXISTS server_id INTEGER,
    ADD COLUMN IF NOT EXISTS plan_version INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS plan_fingerprint VARCHAR(64),
    ADD COLUMN IF NOT EXISTS approval_status VARCHAR(30),
    ADD COLUMN IF NOT EXISTS approval_fingerprint VARCHAR(64),
    ADD COLUMN IF NOT EXISTS approval_comment VARCHAR(2000),
    ADD COLUMN IF NOT EXISTS approval_scope JSON,
    ADD COLUMN IF NOT EXISTS approval_expires_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS execution_status VARCHAR(30),
    ADD COLUMN IF NOT EXISTS verification_status VARCHAR(30),
    ADD COLUMN IF NOT EXISTS rollback_status VARCHAR(30),
    ADD COLUMN IF NOT EXISTS runtime_session_id VARCHAR(128),
    ADD COLUMN IF NOT EXISTS agent_job_id VARCHAR(128);

CREATE INDEX IF NOT EXISTS ix_remediation_plans_server_id
    ON remediation_plans (server_id);
CREATE INDEX IF NOT EXISTS ix_remediation_plans_plan_fingerprint
    ON remediation_plans (plan_fingerprint);

CREATE TABLE IF NOT EXISTS remediation_approvals (
    id INTEGER PRIMARY KEY,
    approval_id VARCHAR(64) NOT NULL UNIQUE,
    plan_id VARCHAR(64) NOT NULL,
    plan_fingerprint VARCHAR(64) NOT NULL,
    status VARCHAR(30) NOT NULL,
    approver VARCHAR(120),
    comment VARCHAR(2000),
    scope JSON NOT NULL DEFAULT '{}',
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    decided_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_remediation_approvals_plan_created
    ON remediation_approvals (plan_id, created_at);
CREATE INDEX IF NOT EXISTS ix_remediation_approvals_status
    ON remediation_approvals (status);

CREATE TABLE IF NOT EXISTS remediation_executions (
    id INTEGER PRIMARY KEY,
    execution_id VARCHAR(64) NOT NULL UNIQUE,
    plan_id VARCHAR(64) NOT NULL,
    action_id VARCHAR(128) NOT NULL,
    server_id INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL,
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    actor VARCHAR(120),
    runtime_session_id VARCHAR(128),
    agent_job_id VARCHAR(128),
    before_evidence_ids JSON NOT NULL DEFAULT '[]',
    after_evidence_ids JSON NOT NULL DEFAULT '[]',
    exit_status INTEGER,
    stdout VARCHAR(12000) NOT NULL DEFAULT '',
    stderr VARCHAR(12000) NOT NULL DEFAULT '',
    error VARCHAR(4000),
    created_at TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSON NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_remediation_executions_plan_created
    ON remediation_executions (plan_id, created_at);
CREATE INDEX IF NOT EXISTS ix_remediation_executions_status
    ON remediation_executions (status);

CREATE TABLE IF NOT EXISTS remediation_verifications (
    id INTEGER PRIMARY KEY,
    verification_id VARCHAR(64) NOT NULL UNIQUE,
    execution_id VARCHAR(64) NOT NULL,
    status VARCHAR(30) NOT NULL,
    before_evidence_ids JSON NOT NULL DEFAULT '[]',
    after_evidence_ids JSON NOT NULL DEFAULT '[]',
    details JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_remediation_verifications_execution_id
    ON remediation_verifications (execution_id);

CREATE TABLE IF NOT EXISTS remediation_rollbacks (
    id INTEGER PRIMARY KEY,
    rollback_id VARCHAR(64) NOT NULL UNIQUE,
    execution_id VARCHAR(64) NOT NULL,
    status VARCHAR(30) NOT NULL,
    before_evidence_ids JSON NOT NULL DEFAULT '[]',
    after_evidence_ids JSON NOT NULL DEFAULT '[]',
    details JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_remediation_rollbacks_execution_id
    ON remediation_rollbacks (execution_id);

CREATE TABLE IF NOT EXISTS remediation_audit_events (
    id INTEGER PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL UNIQUE,
    plan_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(80) NOT NULL,
    actor VARCHAR(120),
    server_id INTEGER,
    runtime_session_id VARCHAR(128),
    agent_job_id VARCHAR(128),
    payload JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_remediation_audit_plan_created
    ON remediation_audit_events (plan_id, created_at);
CREATE INDEX IF NOT EXISTS ix_remediation_audit_event_type
    ON remediation_audit_events (event_type);
