-- Step 3.7: HNSW vector index for cosine distance.
-- CREATE INDEX CONCURRENTLY must not run inside an explicit transaction.

CREATE INDEX CONCURRENTLY IF NOT EXISTS
    ix_retrieval_embedding_hnsw_cosine
ON report_retrieval_documents
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 16,
    ef_construction = 64
);

ANALYZE report_retrieval_documents;
