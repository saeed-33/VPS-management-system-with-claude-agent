# Admin UI Completion

The Admin UI remains FastAPI + Jinja2 + vanilla JavaScript. All writes use
the existing centralized `apiRequest` helper, which adds CSRF, parses JSON or
plain error responses, reports 401/403/4xx/5xx failures, and only updates the
page after a successful request.

## Operational screens

| Screen | Route | Main API | Permission |
|---|---|---|---|
| Servers | `/servers` | `/api/servers`, server test/profile routes | viewer read; admin writes; operator monitoring controls |
| Monitoring profiles | `/monitoring-profiles` | `/api/monitoring-profiles/**` | viewer read; admin writes |
| Investigations | `/investigations` | `/api/investigations/**` | viewer+ |
| Reports | `/reports` | `/api/reports/**` | viewer+ |
| Specialists | `/specialists` | `/api/specialists/**` | viewer read; admin writes |
| Remediation | `/remediation` | `/api/remediation/**` | viewer read; operator approval, sandbox, execution, rollback |
| Policies | `/autonomous-policies` | `/api/autonomous-remediation/policies/**` | viewer read; admin administration |
| Candidates | `/autonomous-candidates` | `/api/autonomous-remediation/candidates` | viewer+; admin draft link |
| History | `/autonomous-history` | candidates + `/history` | viewer+ |
| Decisions | `/autonomous-decisions` | `/decisions` | viewer+ |
| Runtime | `/autonomous-runtime` | policies + `/policies/{id}/runtime` | viewer read; admin resume |
| Reservations | `/autonomous-reservations` | `/executions` | viewer+ read-only |
| Authorizations | `/autonomous-authorizations` | `/authorizations` | viewer+ read-only; secrets omitted |
| Audit | `/audit` | `/autonomous-remediation/audit` | viewer+ |
| System / Safety | `/system` | `/api/system/runtime` | viewer+ read-only |

`/runtime-policies` is retained only as a compatibility redirect to
`/autonomous-runtime`; it no longer presents misleading runtime-only content.

## Safety behavior

Candidates are advisory and can only prefill a disabled policy form. They are
never saved or enabled automatically. Policy creation is Admin-only and the
backend remains the authority for exact action, target, risk, evidence,
sandbox, rollback, rate, and suspension constraints.

Remediation displays plan, issue/plan fingerprints, sandbox validation,
approval, execution, verification, rollback, Evidence IDs, and audit events.
It exposes no arbitrary command, raw SSH, raw SQL, force execution, policy or
sandbox bypass, manual authorization issuance, or authorization replay.

Server safety labels are returned by the backend from persisted description
markers (`safe-remediation-test` + `non-production`, `non-production`,
`production`, or `unclassified`). Hostnames alone never determine safety.

The System / Safety screen displays the global automatic-remediation state,
V1 action/risk limits, Phase 6 sandbox configuration, MCP count, scheduler,
and Admin session security. It intentionally provides no global autonomy
toggle.
