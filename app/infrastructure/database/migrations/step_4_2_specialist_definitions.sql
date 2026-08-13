BEGIN;

CREATE TABLE IF NOT EXISTS specialist_definitions (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    instructions TEXT,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    domains JSON NOT NULL DEFAULT '[]'::json,
    trigger_hints JSON NOT NULL DEFAULT '[]'::json,
    knowledge_topics JSON NOT NULL DEFAULT '[]'::json,
    allowed_tool_ids JSON NOT NULL DEFAULT '[]'::json,
    priority INTEGER NOT NULL DEFAULT 100,
    max_rounds INTEGER NOT NULL DEFAULT 2,
    max_actions INTEGER NOT NULL DEFAULT 4,
    metadata JSON NOT NULL DEFAULT '{}'::json,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_specialist_definitions_slug UNIQUE (slug),
    CONSTRAINT ck_specialist_definitions_max_rounds CHECK (max_rounds >= 1),
    CONSTRAINT ck_specialist_definitions_max_actions CHECK (max_actions >= 0)
);

CREATE INDEX IF NOT EXISTS ix_specialist_definitions_slug ON specialist_definitions (slug);
CREATE INDEX IF NOT EXISTS ix_specialist_definitions_name ON specialist_definitions (name);
CREATE INDEX IF NOT EXISTS ix_specialist_definitions_enabled ON specialist_definitions (enabled);
CREATE INDEX IF NOT EXISTS ix_specialist_definitions_priority ON specialist_definitions (priority);

COMMIT;
