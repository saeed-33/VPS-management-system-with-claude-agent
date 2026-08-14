import pytest
from pydantic import ValidationError

from app.core.config import Settings


def settings(**overrides):
    values = {
        "_env_file": None,
        "postgres_db": "db",
        "postgres_user": "user",
        "postgres_password": "password",
        "default_ssh_private_key_path": "./key",
        "ssh_known_hosts_path": "./known_hosts",
    }
    values.update(overrides)
    return Settings(**values)


def test_development_mode_allows_local_cookie_configuration():
    value = settings(debug=True, admin_session_secret="", admin_session_secure=False)
    assert value.debug is True
    assert value.admin_session_secure is False


def test_production_requires_stable_strong_session_secret():
    with pytest.raises(ValidationError, match="ADMIN_SESSION_SECRET"):
        settings(debug=False, admin_session_secret="", admin_session_secure=True)

    with pytest.raises(ValidationError, match="ADMIN_SESSION_SECRET"):
        settings(debug=False, admin_session_secret="short", admin_session_secure=True)


def test_production_requires_secure_cookie_flag():
    with pytest.raises(ValidationError, match="ADMIN_SESSION_SECURE"):
        settings(
            debug=False,
            admin_session_secret="x" * 64,
            admin_session_secure=False,
        )


def test_production_security_configuration_is_accepted():
    value = settings(
        debug=False,
        admin_session_secret="x" * 64,
        admin_session_secure=True,
    )
    assert value.debug is False
    assert value.admin_session_secure is True
