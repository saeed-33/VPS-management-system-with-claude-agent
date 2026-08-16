-- Migration مملوكة للمشروع: تغيّر schema/persistence contract المطلوب للمراحل التي يسميها اسم الملف.
-- تُشغّل خارج application workflow ولا تحتوي منطق runtime أو authorization.
CREATE TABLE IF NOT EXISTS remediation_plans (
    id INTEGER PRIMARY KEY,
    plan_id VARCHAR(64) NOT NULL UNIQUE,
    investigation_id VARCHAR(64) NOT NULL,
    title VARCHAR(300) NOT NULL,
    problem_summary VARCHAR(4000) NOT NULL,
    proposed_actions JSON NOT NULL DEFAULT '[]',
    diagnosis_claim_ids JSON NOT NULL DEFAULT '[]',
    evidence_ids JSON NOT NULL DEFAULT '[]',
    risk_level VARCHAR(20) NOT NULL,
    rollback_plan VARCHAR(4000),
    status VARCHAR(40) NOT NULL,
    sandbox_result_id VARCHAR(64),
    approval_requested_at TIMESTAMP,
    approved_by VARCHAR(120),
    approved_at TIMESTAMP,
    denial_reason VARCHAR(2000),
    metadata JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_remediation_plans_plan_id
    ON remediation_plans (plan_id);

CREATE INDEX IF NOT EXISTS ix_remediation_plans_investigation_created
    ON remediation_plans (investigation_id, created_at);

CREATE INDEX IF NOT EXISTS ix_remediation_plans_status
    ON remediation_plans (status);

CREATE INDEX IF NOT EXISTS ix_remediation_plans_sandbox_result_id
    ON remediation_plans (sandbox_result_id);

CREATE TABLE IF NOT EXISTS remediation_sandbox_results (
    id INTEGER PRIMARY KEY,
    result_id VARCHAR(64) NOT NULL UNIQUE,
    plan_id VARCHAR(64) NOT NULL,
    status VARCHAR(30) NOT NULL,
    before_evidence_ids JSON NOT NULL DEFAULT '[]',
    after_evidence_ids JSON NOT NULL DEFAULT '[]',
    logs JSON NOT NULL DEFAULT '[]',
    metadata JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_remediation_sandbox_results_result_id
    ON remediation_sandbox_results (result_id);

CREATE INDEX IF NOT EXISTS ix_remediation_sandbox_plan_created
    ON remediation_sandbox_results (plan_id, created_at);
