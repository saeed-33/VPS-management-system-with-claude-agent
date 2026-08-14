-- Phase 8 Admin authentication/RBAC boundary.
-- Passwords are never stored; password_hash contains a scrypt verifier.
-- Session cookies contain opaque tokens while this database stores only
-- their SHA-256 digests. The migration is additive and idempotent.

CREATE TABLE IF NOT EXISTS admin_users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(512) NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_admin_users_role
        CHECK (role IN ('viewer', 'operator', 'admin'))
);
CREATE INDEX IF NOT EXISTS ix_admin_users_active_role
    ON admin_users(is_active, role);

CREATE TABLE IF NOT EXISTS admin_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_digest VARCHAR(64) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_agent VARCHAR(500),
    remote_addr VARCHAR(128)
);
CREATE INDEX IF NOT EXISTS ix_admin_sessions_user_expires
    ON admin_sessions(user_id, expires_at);
CREATE INDEX IF NOT EXISTS ix_admin_sessions_active_expires
    ON admin_sessions(revoked_at, expires_at);

CREATE TABLE IF NOT EXISTS admin_auth_audit_events (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL UNIQUE,
    event_type VARCHAR(80) NOT NULL,
    user_id BIGINT REFERENCES admin_users(id) ON DELETE SET NULL,
    username VARCHAR(120),
    success BOOLEAN NOT NULL DEFAULT TRUE,
    remote_addr VARCHAR(128),
    user_agent VARCHAR(500),
    metadata JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_admin_auth_audit_event_created
    ON admin_auth_audit_events(event_type, created_at);
CREATE INDEX IF NOT EXISTS ix_admin_auth_audit_user_created
    ON admin_auth_audit_events(user_id, created_at);
