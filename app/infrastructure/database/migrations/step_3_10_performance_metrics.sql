BEGIN;

ALTER TABLE report_analyses
    ADD COLUMN IF NOT EXISTS performance_metrics jsonb
    NOT NULL DEFAULT '{}'::jsonb;

COMMIT;
