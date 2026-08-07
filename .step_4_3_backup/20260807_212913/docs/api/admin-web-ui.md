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
app/admin/web/templates/base.html
```

Static files تركب على:

```text
/static
```

من:

```text
app/admin/web/static/
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
