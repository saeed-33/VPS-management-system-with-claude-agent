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

`/specialists` manages user-defined specialist definitions. Phase 4.3 supports create, edit, enable/disable and delete. It does not execute agents.

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
