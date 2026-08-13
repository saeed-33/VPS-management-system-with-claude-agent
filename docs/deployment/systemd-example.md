# systemd Example

هذا مثال توثيقي وليس ملف deployment مفروض على كل البيئات.

```ini
[Unit]
Description=AI VPS Management
After=network-online.target postgresql.service
Wants=network-online.target

[Service]
Type=simple
User=chat-system
Group=chat-system
WorkingDirectory=/opt/chat_system
EnvironmentFile=/opt/chat_system/.env
ExecStart=/usr/local/bin/uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5
TimeoutStopSec=60

# Basic hardening; validate against SSH key/storage requirements.
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

## ملاحظات

- لا تضف `--workers` حاليًا.
- لا تضف `--reload`.
- يجب أن يستطيع مستخدم الخدمة قراءة SSH private key وknown_hosts.
- يفضل تخزين المشروع والـ`.env` بصلاحيات محدودة.
- راجع hardening options قبل تفعيل قيود filesystem إضافية لأنها قد تمنع قراءة مفاتيح SSH أو ملفات التطبيق.

Logs ستذهب إلى journald افتراضيًا ويمكن إدارتها عبر systemd/journald policy.

<!-- PROJECT-DOC-METADATA:BEGIN -->
Document classification: **OPERATIONS**

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
