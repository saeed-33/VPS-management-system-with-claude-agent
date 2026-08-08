BEGIN;

CREATE TABLE IF NOT EXISTS investigations (
    id BIGSERIAL PRIMARY KEY,
    investigation_id VARCHAR(36) NOT NULL UNIQUE,
    server_id BIGINT NOT NULL REFERENCES servers(id) ON DELETE CASCADE,
    report_id BIGINT NOT NULL REFERENCES monitoring_reports(id) ON DELETE CASCADE,
    analysis_id BIGINT NULL REFERENCES report_analyses(id) ON DELETE SET NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'created',
    should_investigate BOOLEAN NOT NULL,
    routing_reasons JSON NOT NULL DEFAULT '[]'::json,
    detected_domains JSON NOT NULL DEFAULT '[]'::json,
    unmatched_issue_indexes JSON NOT NULL DEFAULT '[]'::json,
    registry_size INTEGER NOT NULL,
    candidate_limit INTEGER NOT NULL,
    selection_limit INTEGER NOT NULL,
    max_specialists INTEGER NOT NULL DEFAULT 4,
    max_rounds INTEGER NOT NULL DEFAULT 3,
    max_actions INTEGER NOT NULL DEFAULT 12,
    routing_version VARCHAR(50) NOT NULL DEFAULT 'deterministic-v1',
    metadata JSON NOT NULL DEFAULT '{}'::json,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_investigations_candidate_limit CHECK (candidate_limit >= 1),
    CONSTRAINT ck_investigations_selection_limit CHECK (selection_limit >= 1),
    CONSTRAINT ck_investigations_candidate_selection_limits
        CHECK (candidate_limit >= selection_limit),
    CONSTRAINT ck_investigations_max_specialists CHECK (max_specialists >= 1),
    CONSTRAINT ck_investigations_max_rounds CHECK (max_rounds >= 1),
    CONSTRAINT ck_investigations_max_actions CHECK (max_actions >= 0)
);

CREATE TABLE IF NOT EXISTS investigation_specialist_candidates (
    id BIGSERIAL PRIMARY KEY,
    investigation_id BIGINT NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
    specialist_definition_id BIGINT NULL
        REFERENCES specialist_definitions(id) ON DELETE SET NULL,
    specialist_slug VARCHAR(100) NOT NULL,
    specialist_name VARCHAR(150) NOT NULL,
    score INTEGER NOT NULL,
    priority INTEGER NOT NULL,
    candidate_rank INTEGER NOT NULL,
    is_selected BOOLEAN NOT NULL DEFAULT FALSE,
    selected_rank INTEGER NULL,
    matched_domains JSON NOT NULL DEFAULT '[]'::json,
    matched_trigger_hints JSON NOT NULL DEFAULT '[]'::json,
    matched_issue_indexes JSON NOT NULL DEFAULT '[]'::json,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_investigation_candidate_slug
        UNIQUE (investigation_id, specialist_slug),
    CONSTRAINT ck_investigation_candidates_rank CHECK (candidate_rank >= 1),
    CONSTRAINT ck_investigation_candidates_selected_rank
        CHECK (selected_rank IS NULL OR selected_rank >= 1)
);

CREATE INDEX IF NOT EXISTS ix_investigations_investigation_id
    ON investigations (investigation_id);
CREATE INDEX IF NOT EXISTS ix_investigations_server_created
    ON investigations (server_id, created_at);
CREATE INDEX IF NOT EXISTS ix_investigations_report
    ON investigations (report_id);
CREATE INDEX IF NOT EXISTS ix_investigations_analysis_id
    ON investigations (analysis_id);
CREATE INDEX IF NOT EXISTS ix_investigations_status
    ON investigations (status);
CREATE INDEX IF NOT EXISTS ix_investigation_candidates_investigation_rank
    ON investigation_specialist_candidates (investigation_id, candidate_rank);
CREATE INDEX IF NOT EXISTS ix_investigation_candidates_selected
    ON investigation_specialist_candidates (
        investigation_id,
        is_selected,
        selected_rank
    );
CREATE INDEX IF NOT EXISTS ix_investigation_candidates_specialist_slug
    ON investigation_specialist_candidates (specialist_slug);
CREATE INDEX IF NOT EXISTS ix_investigation_specialist_candidates_specialist_definition_id
    ON investigation_specialist_candidates (specialist_definition_id);

COMMIT;
