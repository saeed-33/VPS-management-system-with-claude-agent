-- Migration مملوكة للمشروع: تغيّر schema/persistence contract المطلوب للمراحل التي يسميها اسم الملف.
-- تُشغّل خارج application workflow ولا تحتوي منطق runtime أو authorization.
BEGIN;

CREATE TABLE IF NOT EXISTS knowledge_documents (
    id BIGSERIAL PRIMARY KEY,
    source_id BIGINT NOT NULL REFERENCES knowledge_sources(id) ON DELETE CASCADE,
    canonical_uri TEXT NOT NULL,
    title VARCHAR(500) NULL,
    media_type VARCHAR(150) NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    content_hash VARCHAR(64) NULL,
    parser_name VARCHAR(100) NULL,
    parser_version VARCHAR(50) NULL,
    page_count INTEGER NULL,
    character_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT NULL,
    metadata JSON NOT NULL DEFAULT '{}'::json,
    fetched_at TIMESTAMPTZ NULL,
    parsed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_knowledge_documents_source_uri UNIQUE (source_id, canonical_uri)
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    source_id BIGINT NOT NULL REFERENCES knowledge_sources(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    section_title VARCHAR(500) NULL,
    page_number INTEGER NULL,
    content TEXT NOT NULL,
    character_count INTEGER NOT NULL,
    token_count INTEGER NULL,
    content_hash VARCHAR(64) NOT NULL,
    metadata JSON NOT NULL DEFAULT '{}'::json,
    search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('simple', coalesce(section_title, '') || ' ' || coalesce(content, ''))
    ) STORED,
    embedding vector(768) NULL,
    embedding_provider VARCHAR(50) NULL,
    embedding_model VARCHAR(150) NULL,
    embedding_dimensions INTEGER NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_knowledge_chunks_document_index UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS ix_knowledge_documents_source_id ON knowledge_documents (source_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_documents_status ON knowledge_documents (status);
CREATE INDEX IF NOT EXISTS ix_knowledge_documents_content_hash ON knowledge_documents (content_hash);
CREATE INDEX IF NOT EXISTS ix_knowledge_documents_source_status ON knowledge_documents (source_id, status);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_document_id ON knowledge_chunks (document_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_source_id ON knowledge_chunks (source_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_content_hash ON knowledge_chunks (content_hash);
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_document ON knowledge_chunks (document_id, chunk_index);

COMMIT;
