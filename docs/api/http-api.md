# HTTP API Reference

Base URL أثناء التطوير:

```text
http://127.0.0.1:8000
```

FastAPI يوفر افتراضيًا:

```text
/openapi.json
/docs
/redoc
/health
```

## ملاحظة أمنية

لا توجد Authentication أو Authorization ظاهرة حاليًا على المسارات الحالية، لذلك لا ينبغي اعتبار الـAPI مناسبًا للتعرض المباشر للإنترنت قبل إضافة طبقة أمنية.

## System

### GET /health

يعيد حالة التطبيق وLLM provider/model عندما يكون التحليل مفعلًا.

## Servers

Prefix: `/api/servers`

- `GET /api/servers` — list servers.
- `GET /api/servers/{server_id}` — get server.
- `POST /api/servers` — create server, `201`.
- `PATCH /api/servers/{server_id}` — partial update.
- `DELETE /api/servers/{server_id}` — delete, `204`.
- `POST /api/servers/{server_id}/test` — SSH connection test.

Server create fields:

```text
name
host
port=22
username
private_key_path
description
monitor_enabled=true
interval_seconds=60
monitoring_profile_id
```

Validation الأساسية: port بين 1 و65535 وinterval_seconds >= 5.

## Monitoring Commands

- `GET /api/commands`
- `GET /api/commands/{command_id}`
- `POST /api/commands`
- `PATCH /api/commands/{command_id}`
- `DELETE /api/commands/{command_id}`

Create fields:

```text
name
command
description
timeout_seconds=20
enabled=true
fingerprint_strategy=full_output
fingerprint_config={}
```

Fingerprint strategies:

```text
full_output
status_only
canonical_lines
error_signature
exclude_output
```

ملاحظة: Update schema الحالي لا يحتوي حقول تعديل `fingerprint_strategy` أو `fingerprint_config`.

## Monitoring Profiles

- `GET /api/monitoring-profiles`
- `GET /api/monitoring-profiles/{profile_id}`
- `POST /api/monitoring-profiles`
- `PATCH /api/monitoring-profiles/{profile_id}`
- `DELETE /api/monitoring-profiles/{profile_id}`
- `GET /api/monitoring-profiles/{profile_id}/commands`
- `POST /api/monitoring-profiles/{profile_id}/commands/{command_id}`
- `PATCH /api/monitoring-profiles/{profile_id}/commands/{command_id}`
- `DELETE /api/monitoring-profiles/{profile_id}/commands/{command_id}`
- `PUT /api/servers/{server_id}/monitoring-profile`

ربط command بالـprofile يستخدم:

```text
execution_order
enabled
custom_timeout_seconds
```

وربط profile بالسيرفر يقبل:

```json
{"profile_id": 3}
```

أو `null` لفصل الـprofile.

## Reports

Prefix: `/api/reports`

### GET /api/reports

Query parameters:

```text
server_id >= 1
status
page >= 1
page_size 1..200
```

### GET /api/reports/{report_id}

يعيد التقرير الكامل مع command executions.

### GET /api/reports/{report_id}/analysis

يعيد التحليل الكامل بما فيه:

```text
provider_name
model_name
status
health_status
summary
issues
positive_findings
recommended_actions
analysis_error
duration_ms
attempts
report_fingerprint
analysis_source
reused_from_analysis_id
retrieval_strategy
retrieval_score
llm_called
```

### GET /api/reports/{report_id}/analysis-sources

يعيد مصادر التحليل مع strategy, similarity, rank, excerpt, metadata وused_in_prompt.

### GET /api/reports/{report_id}/analysis-summary

Endpoint خفيف للاستعلام عن توفر وحالة التحليل.

### GET /api/reports/{report_id}/pdf

يعيد `application/pdf` مع `Content-Disposition` للتنزيل.

## أخطاء شائعة

- `404` — resource missing.
- `409` — duplicate/conflict.
- `422` — validation/invalid input.
- `500` — PDF generation failure.

## التحقق من المسارات

```powershell
uv run python tools/dev/list_routes.py
```

ولحفظ JSON:

```powershell
uv run python tools/dev/list_routes.py --json artifacts/routes.json
```

# Specialists API

See [Specialists Management API](specialists-api.md).

```text
GET    /api/specialists
GET    /api/specialists/{id}
POST   /api/specialists
PATCH  /api/specialists/{id}
PUT    /api/specialists/{id}/enabled
DELETE /api/specialists/{id}
```

## Current Phase 4.20 Boundary

```text
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For canonical current state see `docs/PROJECT_STATUS.md`; for test execution see `docs/testing/TESTING_STRATEGY.md`.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT**

Documentation synchronized: **2026-08-12**

Canonical project state:

```text
Phase 4.20: complete
readiness: ready_for_supervised_operations
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
