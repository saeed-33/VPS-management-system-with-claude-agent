from __future__ import annotations

import os
from pathlib import Path

import pytest
from _pytest.outcomes import Failed

from tests.real_runtime.test_phase7_real_autonomous_acceptance import (
    _load_operational_runtime_env,
)


REQUIRED_ENVIRONMENT_KEYS = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "SSH_KNOWN_HOSTS_PATH",
)


def _write_dotenv(path: Path, **values: str) -> None:
    path.write_text(
        "\n".join(f"{key}={value}" for key, value in values.items()) + "\n",
        encoding="utf-8",
    )


def _clear_runtime_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (*REQUIRED_ENVIRONMENT_KEYS, "DEFAULT_SSH_PRIVATE_KEY_PATH"):
        monkeypatch.delenv(key, raising=False)


def test_process_environment_has_precedence_over_dotenv(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env_path = tmp_path / ".env"
    _write_dotenv(
        env_path,
        POSTGRES_HOST="127.0.0.1",
        POSTGRES_PORT="5432",
        POSTGRES_DB="chat_system",
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD="dotenv-password",
        SSH_KNOWN_HOSTS_PATH="/tmp/known_hosts",
        DEFAULT_SSH_PRIVATE_KEY_PATH="/tmp/dotenv-key",
    )
    _clear_runtime_environment(monkeypatch)
    monkeypatch.setenv("POSTGRES_HOST", "172.18.128.1")
    monkeypatch.setenv("DEFAULT_SSH_PRIVATE_KEY_PATH", "/tmp/exported-key")

    _load_operational_runtime_env(env_path=env_path)

    assert os.environ["POSTGRES_HOST"] == "172.18.128.1"
    assert os.environ["DEFAULT_SSH_PRIVATE_KEY_PATH"] == "/tmp/exported-key"


def test_dotenv_is_used_as_fallback_for_missing_process_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env_path = tmp_path / ".env"
    _write_dotenv(
        env_path,
        POSTGRES_HOST="172.18.128.1",
        POSTGRES_PORT="5432",
        POSTGRES_DB="chat_system",
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD="dotenv-password",
        SSH_KNOWN_HOSTS_PATH="/tmp/known_hosts",
    )
    _clear_runtime_environment(monkeypatch)

    _load_operational_runtime_env(env_path=env_path)

    assert os.environ["POSTGRES_HOST"] == "172.18.128.1"
    assert os.environ["POSTGRES_PASSWORD"] == "dotenv-password"


def test_missing_required_environment_value_fails_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env_path = tmp_path / ".env"
    _write_dotenv(
        env_path,
        POSTGRES_HOST="172.18.128.1",
        POSTGRES_PORT="5432",
        POSTGRES_DB="chat_system",
        POSTGRES_USER="postgres",
        SSH_KNOWN_HOSTS_PATH="/tmp/known_hosts",
    )
    _clear_runtime_environment(monkeypatch)

    with pytest.raises(Failed, match="POSTGRES_PASSWORD"):
        _load_operational_runtime_env(env_path=env_path)
