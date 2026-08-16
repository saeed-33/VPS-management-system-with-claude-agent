-- Migration مملوكة للمشروع: تغيّر schema/persistence contract المطلوب للمراحل التي يسميها اسم الملف.
-- تُشغّل خارج application workflow ولا تحتوي منطق runtime أو authorization.
CREATE INDEX IF NOT EXISTS
    ix_knowledge_chunks_search_vector_gin
ON knowledge_chunks
USING gin (search_vector);

CREATE INDEX IF NOT EXISTS
    ix_knowledge_chunks_embedding_hnsw_cosine
ON knowledge_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 16,
    ef_construction = 64
);

ANALYZE knowledge_chunks;
