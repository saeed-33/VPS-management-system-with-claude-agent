-- Migration مملوكة للمشروع: تغيّر schema/persistence contract المطلوب للمراحل التي يسميها اسم الملف.
-- تُشغّل خارج application workflow ولا تحتوي منطق runtime أو authorization.
BEGIN;

ALTER TABLE report_analyses
    ADD COLUMN IF NOT EXISTS performance_metrics jsonb
    NOT NULL DEFAULT '{}'::jsonb;

COMMIT;
