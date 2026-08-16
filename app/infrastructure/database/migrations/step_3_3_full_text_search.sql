-- Migration مملوكة للمشروع: تغيّر schema/persistence contract المطلوب للمراحل التي يسميها اسم الملف.
-- تُشغّل خارج application workflow ولا تحتوي منطق runtime أو authorization.
BEGIN;

ALTER TABLE report_retrieval_documents
    ADD COLUMN IF NOT EXISTS search_vector tsvector
    GENERATED ALWAYS AS (
        to_tsvector(
            'simple',
            coalesce(normalized_text, '')
        )
    ) STORED;

CREATE INDEX IF NOT EXISTS ix_retrieval_search_vector_gin
    ON report_retrieval_documents
    USING gin (search_vector);

CREATE INDEX IF NOT EXISTS ix_retrieval_scope
    ON report_retrieval_documents (
        server_id,
        monitoring_profile_id,
        command_set_hash
    );

COMMIT;
