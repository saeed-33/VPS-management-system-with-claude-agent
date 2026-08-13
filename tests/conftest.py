import os


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
