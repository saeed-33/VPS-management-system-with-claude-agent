# Admin Web UI

الواجهة الحالية مبنية بـFastAPI + Jinja2.

## صفحات الويب

| URL | Template |
|---|---|
| `/` | `dashboard.html` |
| `/servers` | `servers.html` |
| `/commands` | `commands.html` |
| `/monitoring-profiles` | `monitoring_profiles.html` |
| `/reports` | `reports.html` |
| `/reports/{report_id}` | `report_details.html` |
| `/remediation` | `remediation.html` |

القالب الأساسي:

```text
app/interfaces/admin/web/templates/base.html
```

Static files تركب على:

```text
/static
```

من:

```text
app/interfaces/admin/web/static/
```

## العلاقة مع API

```text
Browser
  -> page route / Jinja2
  -> JavaScript/forms
  -> /api/servers
  -> /api/commands
  -> /api/monitoring-profiles
  -> /api/reports
  -> /api/remediation (plan review, approval, execution, rollback, audit)
```

صفحة تفاصيل التقرير تعتمد منطقيًا على:

```text
GET /api/reports/{id}
GET /api/reports/{id}/analysis
GET /api/reports/{id}/analysis-sources
GET /api/reports/{id}/analysis-summary
GET /api/reports/{id}/pdf
```

## OpenAPI

Web router يستخدم `include_in_schema=False`، لذلك صفحات HTML لا تظهر في Swagger، بينما `/api/*` و`/health` تظهر افتراضيًا.

## Security

لا توجد Authentication/Authorization ظاهرة حاليًا في routes أو `app.main`. هذا baseline لبيئة موثوقة، وليس توصيف نشر Internet-facing آمن.

## Specialists

`/specialists` manages user-defined Specialist definitions, including create,
edit, enable/disable, delete, and bounded tool-ID configuration. It does not
execute agents directly.

## Supervised remediation

The `/remediation` page reads the canonical `/api/remediation` routes. The
API exposes persisted plan review, approval/rejection, deliberate execution,
rollback, and append-only audit events. The operator must provide an explicit
actor; this repository does not provide authentication/RBAC.

```text
GET  /api/remediation
GET  /api/remediation/{plan_id}
GET  /api/remediation/{plan_id}/audit
POST /api/remediation/{plan_id}/approval
POST /api/remediation/{plan_id}/approval/{approval_id}/approve
POST /api/remediation/{plan_id}/approval/{approval_id}/reject
POST /api/remediation/{plan_id}/execute
POST /api/remediation/{plan_id}/rollback
```

Execution remains blocked unless the approval is persisted, unexpired, and
fingerprint-matched; automatic remediation remains disabled.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **CURRENT_CANONICAL**

Documentation synchronized: **2026-08-13**

Canonical project state:

```text
Phase 5: complete / closed
Phase 5 readiness: 13/13 PASS
Phase 6: implemented / not closed
Phase 6 readiness: BLOCKED_BY_SANDBOX_RUNTIME
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
<!-- PROJECT-DOC-METADATA:END -->
