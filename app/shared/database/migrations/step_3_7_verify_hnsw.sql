-- Step 3.7 verification helper.
-- Replace <VECTOR_LITERAL> with a valid 768-dimensional vector literal.

SET LOCAL hnsw.ef_search = 100;

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    id,
    report_id,
    analysis_id,
    1 - (embedding <=> '<VECTOR_LITERAL>'::vector) AS similarity
FROM report_retrieval_documents
WHERE server_id = 1
  AND (embedding <=> '<VECTOR_LITERAL>'::vector) <= (1 - 0.72)
ORDER BY embedding <=> '<VECTOR_LITERAL>'::vector
LIMIT 5;
