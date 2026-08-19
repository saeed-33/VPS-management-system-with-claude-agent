"""Tests for test runtime environment.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from _pytest.outcomes import Failed

from tests.acceptance.external_runtime.test_real_claude_ollama_mcp_cycle import (
    _restore_operational_database_env,
)


def _write_dotenv(path: Path, **values: str) -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى _write_dotenv؛ المدخلات المهمة: path.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى _clear_database_environment؛ المدخلات المهمة: monkeypatch.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_explicit_database_environment_wins_over_dotenv؛ المدخلات المهمة: monkeypatch، tmp_path.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_dotenv_is_fallback_when_database_environment_is_absent؛ المدخلات المهمة: monkeypatch، tmp_path.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_missing_dotenv_database_value_fails_closed؛ المدخلات المهمة: monkeypatch، tmp_path.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
