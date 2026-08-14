from __future__ import annotations

import os
from pathlib import Path

import pytest
from _pytest.outcomes import Failed

from tests.real_runtime.test_c14_11_claude_ollama_mcp_acceptance import (
    _restore_operational_database_env,
)


def _write_dotenv(path: Path, **values: str) -> None:
    path.write_text(
        "\n".join(
            f"{key}={value}"
            for key, value in values.items()
        )
        + "\n",
        encoding="utf-8",
    )


def _clear_database_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for key in (
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ):
        monkeypatch.delenv(key, raising=False)


def test_explicit_database_environment_wins_over_dotenv(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_path = tmp_path / ".env"
    _write_dotenv(
        env_path,
        POSTGRES_HOST="127.0.0.1",
        POSTGRES_PORT="5432",
        POSTGRES_DB="chat_system",
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD="dotenv-password",
    )
    _clear_database_environment(monkeypatch)
    monkeypatch.setenv("POSTGRES_HOST", "172.18.128.1")
    monkeypatch.setenv("POSTGRES_PASSWORD", "explicit-password")

    _restore_operational_database_env(env_path=env_path)

    assert os.environ["POSTGRES_HOST"] == "172.18.128.1"
    assert os.environ["POSTGRES_PASSWORD"] == "explicit-password"
    assert os.environ["POSTGRES_PORT"] == "5432"


def test_dotenv_is_fallback_when_database_environment_is_absent(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_path = tmp_path / ".env"
    _write_dotenv(
        env_path,
        POSTGRES_HOST="172.18.128.1",
        POSTGRES_PORT="5432",
        POSTGRES_DB="chat_system",
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD="dotenv-password",
    )
    _clear_database_environment(monkeypatch)

    _restore_operational_database_env(env_path=env_path)

    assert os.environ["POSTGRES_HOST"] == "172.18.128.1"
    assert os.environ["POSTGRES_PASSWORD"] == "dotenv-password"


def test_missing_dotenv_database_value_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_path = tmp_path / ".env"
    _write_dotenv(
        env_path,
        POSTGRES_HOST="172.18.128.1",
        POSTGRES_PORT="5432",
        POSTGRES_DB="chat_system",
        POSTGRES_USER="postgres",
    )
    _clear_database_environment(monkeypatch)

    with pytest.raises(
        Failed,
        match="POSTGRES_PASSWORD",
    ):
        _restore_operational_database_env(env_path=env_path)
