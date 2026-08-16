-- Migration مملوكة للمشروع: تغيّر schema/persistence contract المطلوب للمراحل التي يسميها اسم الملف.
-- تُشغّل خارج application workflow ولا تحتوي منطق runtime أو authorization.
BEGIN;

CREATE TABLE IF NOT EXISTS knowledge_sources (
    id BIGSERIAL PRIMARY KEY,
    slug VARCHAR(120) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    source_type VARCHAR(30) NOT NULL,
    source_uri TEXT NULL,
    inline_content TEXT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    domains JSON NOT NULL DEFAULT '[]'::json,
    specialist_slugs JSON NOT NULL DEFAULT '[]'::json,
    tags JSON NOT NULL DEFAULT '[]'::json,
    priority INTEGER NOT NULL DEFAULT 100,
    metadata JSON NOT NULL DEFAULT '{}'::json,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_knowledge_sources_priority
        CHECK (priority >= 0)
);

CREATE INDEX IF NOT EXISTS ix_knowledge_sources_slug
    ON knowledge_sources (slug);

CREATE INDEX IF NOT EXISTS ix_knowledge_sources_name
    ON knowledge_sources (name);

CREATE INDEX IF NOT EXISTS ix_knowledge_sources_source_type
    ON knowledge_sources (source_type);

CREATE INDEX IF NOT EXISTS ix_knowledge_sources_enabled
    ON knowledge_sources (enabled);

CREATE INDEX IF NOT EXISTS ix_knowledge_sources_priority
    ON knowledge_sources (priority);

COMMIT;
