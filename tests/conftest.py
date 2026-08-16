"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import os


_REAL_RUNTIME_ENABLED = (
    os.getenv(
        "AI_VPS_RUN_REAL_RUNTIME_TESTS",
        "",
    ).strip()
    == "1"
)

if not _REAL_RUNTIME_ENABLED:
    os.environ.setdefault("POSTGRES_DB", "test_db")
    os.environ.setdefault("POSTGRES_USER", "test_user")
    os.environ.setdefault("POSTGRES_PASSWORD", "test_password")
os.environ.setdefault(
    "DEFAULT_SSH_PRIVATE_KEY_PATH",
    "./.test/id_rsa",
)
os.environ.setdefault(
    "SSH_KNOWN_HOSTS_PATH",
    "./.test/known_hosts",
)
os.environ.setdefault("LLM_ENABLED", "false")
os.environ.setdefault("CLAUDE_RUNTIME_ENABLED", "false")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("ADMIN_SESSION_SECRET", "test-only-admin-session-secret-32-chars")
os.environ.setdefault("ADMIN_SESSION_SECURE", "false")
