"""
فحص جاهزية بيئة التحقق المعزولة المحلية.

يتحقق وقت التشغيل من المسار والأدوات المطلوبة وحدود البيئة، ويعيد نتيجة منظمة
توضح إن كانت المعالجة التجريبية قابلة للتنفيذ.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from app.core.contracts.sandbox_validation.sandbox_runtime_check import SandboxRuntimeCheck


class NativeSandboxRuntime:
    """
    يفحص قدرة البيئة المحلية على تشغيل تحقق معزول بالمتطلبات المحددة.
    """

    def __init__(self, *, attestation_file: str | Path | None = None, require_wsl2: bool = True) -> None:
        """
        يهيئ فاحص البيئة مع إمكانية تمرير إعدادات التطبيق المحملة من ملف الإعداد.

        يبقى متغير البيئة مسارًا احتياطيًا للتشغيل المباشر وأدوات القبول، لكن
        التطبيق الرئيسي لا يعتمد على أن تقوم مكتبة الإعدادات بتصديره إلى البيئة.
        """
        self._attestation_file = Path(attestation_file) if attestation_file else None
        self._require_wsl2 = require_wsl2

    def check(self) -> SandboxRuntimeCheck:
        """
        يفحص وجود runtime والأدوات والمسارات المطلوبة ويعيد نتيجة جاهزية البيئة المعزولة.
        """
        path_value = str(self._attestation_file) if self._attestation_file else os.getenv(
            "PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE", ""
        ).strip()
        if not path_value:
            return SandboxRuntimeCheck(False, "claude-native-sandbox", "attestation_file_missing")
        path = Path(path_value)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return SandboxRuntimeCheck(False, "claude-native-sandbox", f"attestation_unreadable:{type(exc).__name__}")
        required = {
            "sandboxed": True,
            "project_path_accessible": True,
            "sensitive_path_inaccessible": True,
            "unsandboxed_escape_unavailable": True,
        }
        if any(payload.get(key) != value for key, value in required.items()):
            return SandboxRuntimeCheck(False, "claude-native-sandbox", "attestation_requirements_not_met", payload)
        if self._require_wsl2 and not os.getenv("WSL_DISTRO_NAME", "").strip():
            return SandboxRuntimeCheck(False, "claude-native-sandbox", "wsl2_runtime_not_detected", payload)
        return SandboxRuntimeCheck(True, "claude-native-sandbox", evidence=payload)
