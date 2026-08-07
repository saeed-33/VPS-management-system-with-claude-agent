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

يمكن تنفيذ ذلك أولًا عبر reverse proxy/VPN، ثم لاحقًا داخل التطبيق.

### API documentation

FastAPI يعرض افتراضيًا:

```text
/docs
/redoc
/openapi.json
```

في شبكة موثوقة هذا مفيد. في نشر عام يجب تحديد هل ستبقى متاحة ومن يملك الوصول إليها.

## Secrets

أسرار يجب ألا تدخل Git:

- `POSTGRES_PASSWORD`
- `OPENAI_API_KEY`
- SSH private keys
- أي tokens مستقبلية

استخدم `.env` محليًا فقط أو secret manager في بيئة الإنتاج.

`.env.example` يجب أن يحتوي أسماء الإعدادات وقيمًا غير سرية فقط.

## SSH trust boundary

المشروع يستطيع الاتصال بخوادم عبر SSH وتنفيذ Monitor Commands، لذلك SSH هو trust boundary حساس.

القواعد المقترحة:

1. dedicated monitoring account.
2. least privilege.
3. لا root افتراضيًا.
4. مفتاح منفصل لهذا التطبيق.
5. حماية الملف من مستخدمين آخرين.
6. Known Hosts verification.
7. مراجعة Monitor Commands قبل تفعيلها.
8. لا تسمح للمستخدم غير الموثوق بإنشاء أو تعديل command text.

هذه النقطة ستصبح أهم عند بناء Specialist Agents.

## Database

- Role مخصص للتطبيق.
- لا تستخدم postgres superuser يوميًا.
- اسمح بالاتصال فقط من host/network المطلوبة.
- TLS لقاعدة بعيدة حسب البيئة.
- backup مشفر عند احتوائه بيانات حساسة.
- retention policy للتقارير وstdout/stderr لأن outputs قد تحتوي معلومات حساسة.

## LLM data boundary

Monitoring reports قد تحتوي:

- hostnames.
- process names.
- filesystem paths.
- log fragments.
- internal IPs.
- command output.

عند استخدام provider خارجي يجب اعتبار إرسال prompt انتقالًا للبيانات خارج البنية المحلية، وتحديد policy مناسبة للبيئة.

## Web layer

الحالة الحالية لا تظهر طبقة:

- CSRF policy مخصصة.
- session authentication.
- RBAC.
- rate limiting.

إلى أن تضاف هذه الطبقات، أبق التطبيق خلف network control/reverse proxy موثوق.

## Debug mode

في الإنتاج:

```env
DEBUG=false
```

ولا تستخدم Uvicorn reload.

## Error exposure

تجنب مستقبلاً إعادة stack traces أو secrets إلى HTTP clients. API الحالي يستخدم `HTTPException` برسائل محددة، لكن يجب مراجعة أي endpoints جديدة.

## Logging

لا تسجل:

- private key contents.
- DB passwords.
- API keys.
- Authorization headers.

Command stdout/stderr المحفوظ في قاعدة البيانات جزء من بيانات النظام ويحتاج access control وretention.

## Dependency security

قبل release production:

```powershell
uv sync --frozen
uv run python -m pytest
```

ويفضل إضافة dependency vulnerability scanning إلى CI مستقبلًا.

## Multi-Agent future security

قبل السماح للوكلاء بأي diagnostics:

```text
LLM proposes action
       |
Tool Registry
       |
Parameter validation
       |
Policy Engine
       |
Read-only execution
```

لا يجب أن يكون الـLLM قادرًا على إرسال arbitrary shell مباشرة إلى SSH executor.

Remediation يجب أن تبقى مرحلة منفصلة عن diagnostics.
