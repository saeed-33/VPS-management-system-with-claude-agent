CREATE TABLE IF NOT EXISTS agent_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL UNIQUE,
    job_type VARCHAR(80) NOT NULL,
    server_id INTEGER NULL,
    status VARCHAR(30) NOT NULL,
    claude_session_id VARCHAR(120) NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL,
    error_code VARCHAR(80) NULL,
    error_message VARCHAR(2000) NULL,
    turn_count INTEGER NOT NULL DEFAULT 0,
    tool_call_count INTEGER NOT NULL DEFAULT 0,
    usage_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_agent_jobs_turn_count
        CHECK (turn_count >= 0),
    CONSTRAINT ck_agent_jobs_tool_call_count
        CHECK (tool_call_count >= 0)
);

CREATE INDEX IF NOT EXISTS ix_agent_jobs_job_id
    ON agent_jobs (job_id);

CREATE INDEX IF NOT EXISTS ix_agent_jobs_claude_session_id
    ON agent_jobs (claude_session_id);

CREATE INDEX IF NOT EXISTS ix_agent_jobs_status
    ON agent_jobs (status);

CREATE INDEX IF NOT EXISTS ix_agent_jobs_type_status_created
    ON agent_jobs (job_type, status, created_at);

CREATE INDEX IF NOT EXISTS ix_agent_jobs_server_created
    ON agent_jobs (server_id, created_at);
