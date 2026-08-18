"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.remediation.sandbox_runtime.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import json

from app.capabilities.remediation.sandbox_runtime import NativeSandboxRuntime


def test_native_sandbox_runtime_fails_closed_without_attestation(monkeypatch):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_native_sandbox_runtime_fails_closed_without_attestation؛ المدخلات المهمة: monkeypatch.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    monkeypatch.delenv("PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE", raising=False)
    assert NativeSandboxRuntime().check().available is False


def test_native_sandbox_runtime_requires_all_isolation_claims(tmp_path, monkeypatch):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_native_sandbox_runtime_requires_all_isolation_claims؛ المدخلات المهمة: tmp_path، monkeypatch.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    path = tmp_path / "attestation.json"
    path.write_text(json.dumps({"sandboxed": True}), encoding="utf-8")
    monkeypatch.setenv("PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE", str(path))
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
    result = NativeSandboxRuntime().check()
    assert result.available is False


def test_native_sandbox_runtime_accepts_complete_attestation_in_wsl(tmp_path, monkeypatch):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_native_sandbox_runtime_accepts_complete_attestation_in_wsl؛ المدخلات المهمة: tmp_path، monkeypatch.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    path = tmp_path / "attestation.json"
    path.write_text(json.dumps({
        "sandboxed": True,
        "project_path_accessible": True,
        "sensitive_path_inaccessible": True,
        "unsandboxed_escape_unavailable": True,
    }), encoding="utf-8")
    monkeypatch.setenv("PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE", str(path))
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
    assert NativeSandboxRuntime().check().available is True


def test_native_sandbox_runtime_accepts_application_configured_attestation(tmp_path, monkeypatch):
    """
    يثبت أن إعدادات التطبيق تكفي لتحديد ملف الشهادة حتى عندما لا يكون المتغير مصدّرًا.
    """
    path = tmp_path / "configured-attestation.json"
    path.write_text(json.dumps({
        "sandboxed": True,
        "project_path_accessible": True,
        "sensitive_path_inaccessible": True,
        "unsandboxed_escape_unavailable": True,
    }), encoding="utf-8")
    monkeypatch.delenv("PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE", raising=False)
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")

    assert NativeSandboxRuntime(attestation_file=path).check().available is True
