"""
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
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى _write_dotenv؛ المدخلات المهمة: path.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    path.write_text(
        "\n".join(f"{key}={value}" for key, value in values.items()) + "\n",
        encoding="utf-8",
    )


def _clear_runtime_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى _clear_runtime_environment؛ المدخلات المهمة: monkeypatch.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    for key in (*REQUIRED_ENVIRONMENT_KEYS, "DEFAULT_SSH_PRIVATE_KEY_PATH"):
        monkeypatch.delenv(key, raising=False)


def test_process_environment_has_precedence_over_dotenv(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_process_environment_has_precedence_over_dotenv؛ المدخلات المهمة: monkeypatch، tmp_path.
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_dotenv_is_used_as_fallback_for_missing_process_values؛ المدخلات المهمة: monkeypatch، tmp_path.
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
        SSH_KNOWN_HOSTS_PATH="/tmp/known_hosts",
    )
    _clear_runtime_environment(monkeypatch)

    _load_operational_runtime_env(env_path=env_path)

    assert os.environ["POSTGRES_HOST"] == "172.18.128.1"
    assert os.environ["POSTGRES_PASSWORD"] == "dotenv-password"


def test_missing_required_environment_value_fails_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_missing_required_environment_value_fails_closed؛ المدخلات المهمة: monkeypatch، tmp_path.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
