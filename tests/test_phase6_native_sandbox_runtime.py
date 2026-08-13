from __future__ import annotations

import json

from app.capabilities.remediation.sandbox_runtime import NativeSandboxRuntime


def test_native_sandbox_runtime_fails_closed_without_attestation(monkeypatch):
    monkeypatch.delenv("PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE", raising=False)
    assert NativeSandboxRuntime().check().available is False


def test_native_sandbox_runtime_requires_all_isolation_claims(tmp_path, monkeypatch):
    path = tmp_path / "attestation.json"
    path.write_text(json.dumps({"sandboxed": True}), encoding="utf-8")
    monkeypatch.setenv("PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE", str(path))
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
    result = NativeSandboxRuntime().check()
    assert result.available is False


def test_native_sandbox_runtime_accepts_complete_attestation_in_wsl(tmp_path, monkeypatch):
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
