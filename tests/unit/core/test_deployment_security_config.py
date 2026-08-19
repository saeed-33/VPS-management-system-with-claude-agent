"""Tests for test deployment security config.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.config.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import pytest
from pydantic import ValidationError

from app.core.config import Settings


def settings(**overrides):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى settings؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_development_mode_allows_local_cookie_configuration؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    value = settings(debug=True, admin_session_secret="", admin_session_secure=False)
    assert value.debug is True
    assert value.admin_session_secure is False


def test_production_requires_stable_strong_session_secret():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_production_requires_stable_strong_session_secret؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    with pytest.raises(ValidationError, match="ADMIN_SESSION_SECRET"):
        settings(debug=False, admin_session_secret="", admin_session_secure=True)

    with pytest.raises(ValidationError, match="ADMIN_SESSION_SECRET"):
        settings(debug=False, admin_session_secret="short", admin_session_secure=True)


def test_production_requires_secure_cookie_flag():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_production_requires_secure_cookie_flag؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    with pytest.raises(ValidationError, match="ADMIN_SESSION_SECURE"):
        settings(
            debug=False,
            admin_session_secret="x" * 64,
            admin_session_secure=False,
        )


def test_production_security_configuration_is_accepted():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_production_security_configuration_is_accepted؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    value = settings(
        debug=False,
        admin_session_secret="x" * 64,
        admin_session_secure=True,
    )
    assert value.debug is False
    assert value.admin_session_secure is True
