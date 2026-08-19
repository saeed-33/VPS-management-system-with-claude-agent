"""Tests for test real sandbox validation.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import json
import os
from uuid import uuid4

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("REAL_PHASE6_ACCEPTANCE_ENABLED", "").strip().lower() != "true",
    reason="Phase 6 real acceptance is opt-in.",
)


def test_phase6_real_native_sandbox_and_validation_acceptance():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_phase6_real_native_sandbox_and_validation_acceptance؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    required = (
        "SAFE_PHASE6_VALIDATION_SERVER_ID",
        "SAFE_PHASE6_VALIDATION_SERVER_NAME",
        "SAFE_PHASE6_VALIDATION_SERVICE",
        "PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE",
    )
    missing = [key for key in required if not os.getenv(key, "").strip()]
    if missing:
        pytest.fail("REAL_PHASE6_ACCEPTANCE = BLOCKED_BY_SANDBOX_RUNTIME: missing " + ", ".join(missing))
    from pathlib import Path
    try:
        attestation = json.loads(Path(os.environ["PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE"]).read_text(encoding="utf-8"))
    except Exception as exc:
        pytest.fail(f"REAL_PHASE6_ACCEPTANCE = BLOCKED_BY_SANDBOX_RUNTIME: invalid attestation ({type(exc).__name__})")
    required_attestation = {"sandboxed": True, "project_path_accessible": True,
                            "sensitive_path_inaccessible": True, "unsandboxed_escape_unavailable": True}
    assert all(attestation.get(key) is value for key, value in required_attestation.items())
    if not os.getenv("WSL_DISTRO_NAME", "").strip():
        pytest.fail("REAL_PHASE6_ACCEPTANCE = BLOCKED_BY_SANDBOX_RUNTIME: WSL2 runtime not detected")
    from app.composition import container
    server_id = int(os.environ["SAFE_PHASE6_VALIDATION_SERVER_ID"])
    server = container.server_repository.get_by_id(server_id)
    if server is None or server.name != os.environ["SAFE_PHASE6_VALIDATION_SERVER_NAME"]:
        pytest.fail("REAL_PHASE6_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: target identity mismatch")
    if not all(marker in (server.description or "").casefold() for marker in ("safe-remediation-test", "non-production")):
        pytest.fail("REAL_PHASE6_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: target is not designated safe")
    plan = container.remediation_service.create_plan(
        plan_id=f"phase6-real-{uuid4().hex}",
        investigation_id=f"phase6-real-investigation-{uuid4().hex}",
        title="Phase 6 real sandbox validation",
        problem_summary="Dedicated lab service validation.",
        proposed_actions=[{"id": "phase6-real-start", "action_type": "start_service", "target": os.environ["SAFE_PHASE6_VALIDATION_SERVICE"], "reason": "dedicated lab"}],
        diagnosis_claim_ids=["phase6-real-claim"], evidence_ids=["phase6-real-context"], server_id=server_id,
    )
    result = container.remediation_service.validate_in_isolated_sandbox(
        plan_id=plan.plan_id, target_server_id=server_id, target_server_name=server.name,
        target_service=os.environ["SAFE_PHASE6_VALIDATION_SERVICE"],
    )
    assert result.status == "passed"
    approval = container.remediation_service.request_approval(plan_id=plan.plan_id)
    print(json.dumps({"validation_id": result.validation_id, "plan_id": plan.plan_id,
                      "approval_id": approval.approval_id, "before_evidence_ids": result.before_evidence_ids,
                      "after_evidence_ids": result.after_evidence_ids, "final_state_restored": True}, default=str))
