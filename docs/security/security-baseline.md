# Security Baseline

## Scope

هذه ليست شهادة أن المشروع production-secure. هي baseline يوضح ما هو موجود وما يجب تأمينه قبل نشره خارج شبكة موثوقة.

## الحالة الحالية

### Authentication / Authorization

لا توجد حاليًا Authentication/Authorization واضحة على Admin UI أو `/api/*`.

**النتيجة:** لا تعرض التطبيق مباشرة للإنترنت.

الحد الأدنى قبل exposure:

```text
TLS
+
Authentication
+
Authorization
+
Network restrictions
```

### Secrets

أسرار يجب ألا تدخل Git:

- `POSTGRES_PASSWORD`
- `OPENAI_API_KEY`
- SSH private keys
- أي tokens مستقبلية

استخدم `.env` محليًا فقط أو secret manager في بيئة الإنتاج.

## SSH trust boundary

المشروع يستطيع الاتصال بخوادم عبر SSH، لذلك SSH هو trust boundary حساس.

قواعد التشغيل الأساسية:

1. dedicated monitoring account.
2. least privilege.
3. لا root افتراضيًا.
4. مفتاح منفصل لهذا التطبيق.
5. Known Hosts verification.
6. مراجعة Monitor Commands.
7. حماية credentials وprivate keys.

## Multi-Agent diagnostic boundary — implemented

Phase 4.12–4.17 تطبق مسار diagnostics مقيدًا:

```text
LLM structured Tool request
       |
Diagnostic Tool Registry
       |
typed parameter validation
       |
Diagnostic Policy Engine
       |
approved execution envelope
       |
Evidence Collection
       |
known read-only SSH implementation
```

الـLLM لا يرسل shell command خامًا إلى SSH executor.

### Tool permissions

كل Specialist يملك `allowed_tool_ids` محددة.

الـPolicy يرفض:

```text
unknown Tool
unassigned Tool
unsupported risk
invalid arguments
round budget overflow
action budget overflow
```

### Read-only boundary

Phase 4 تسمح فقط بأدوات `read_only`.

```text
NO automatic restart
NO kill process
NO config modification
NO package installation
NO reboot
NO firewall changes
NO arbitrary shell
```

Remediation تبقى Phase 5 منفصلة بصلاحيات وموافقة وتدقيق وrollback مختلف.

### Evidence provenance

Evidence الناتجة عن diagnostic execution تحفظ metadata تشخيصية مثل:

```text
server
Specialist
Tool
approved command
exit status
duration
timeout/output limits
timestamps
```

لا تُنسخ credentials أو private-key paths إلى Evidence metadata.

### Dynamic Specialists

تعريف Specialist بيانات يديرها operator، لكنه لا يمنح نفسه صلاحية تنفيذ Tool غير مسجلة.

توصيات `recommended_next_specialists` advisory فقط. الـLLM لا يستطيع إنشاء Specialist executable؛ أي secondary Specialist يجب أن يكون موجودًا ومفعّلًا في Registry وأن يمر بقيود الميزانية ومنع التكرار.

### LangGraph

LangGraph ينظم workflow فقط. لا يملك سلطة تجاوز:

```text
Registry
Tool allow-list
Policy Engine
Evidence provenance
SSH implementation
Investigation budgets
```

## Database

- Role مخصص للتطبيق.
- لا تستخدم postgres superuser يوميًا.
- اسمح بالاتصال فقط من host/network المطلوبة.
- TLS لقاعدة بعيدة حسب البيئة.
- backup مشفر عند احتوائه بيانات حساسة.
- retention policy للتقارير وstdout/stderr لأن outputs قد تحتوي معلومات حساسة.

## LLM data boundary

Monitoring reports وEvidence قد تحتوي:

- hostnames.
- process names.
- filesystem paths.
- log fragments.
- internal IPs.
- command output.

عند استخدام provider خارجي يجب اعتبار إرسال prompt انتقالًا للبيانات خارج البنية المحلية وتحديد policy مناسبة للبيئة.

## Web layer

الحالة الحالية لا تظهر طبقة مكتملة لـ:

- session authentication.
- RBAC.
- rate limiting.
- CSRF policy مخصصة.

إلى أن تضاف هذه الطبقات، أبق التطبيق خلف network control/reverse proxy موثوق.

## Production reminders

```env
DEBUG=false
```

لا تستخدم Uvicorn reload في الإنتاج.

لا تسجل private keys أو DB passwords أو API keys أو Authorization headers.

قبل release production:

```powershell
uv sync --frozen
uv run python -m pytest
```

ويفضل إضافة dependency vulnerability scanning إلى CI.
