"""Tests for test sandbox validation.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.remediation.execution، app.capabilities.remediation.service، app.core.contracts.sandbox_validation، app.infrastructure.database.base، app.infrastructure.database.models.server، app.infrastructure.database.models.remediation.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.contracts.remediation.service_state_observation import ServiceStateObservation
from app.core.contracts.remediation.write_command_result import WriteCommandResult
from app.capabilities.remediation.service.remediation_service import RemediationService
from app.core.contracts.sandbox_validation.sandbox_runtime_check import SandboxRuntimeCheck
from app.core.contracts.sandbox_validation.sandbox_validation_status import SandboxValidationStatus
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.server.server import ServerModel
from app.infrastructure.database.models.remediation.approval import RemediationApprovalModel
from app.infrastructure.database.models.remediation.audit_event import RemediationAuditEventModel
from app.infrastructure.database.models.remediation.evidence import RemediationEvidenceModel
from app.infrastructure.database.models.remediation.execution import RemediationExecutionModel
from app.infrastructure.database.models.remediation.plan import RemediationPlanModel
from app.infrastructure.database.models.remediation.rollback import RemediationRollbackModel
from app.infrastructure.database.models.remediation.sandbox_result import RemediationSandboxResultModel
from app.infrastructure.database.models.remediation.verification import RemediationVerificationModel
from app.infrastructure.database.models.remediation.sandbox_validation import SandboxValidationModel
from app.infrastructure.database.repositories.remediation_repository.repository import RemediationRepository


class FakeServerRepository:
    """
    يمثل FakeServerRepository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, server):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: server.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.server = server

    def get_by_id(self, server_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_by_id؛ المدخلات المهمة: server_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.server if self.server.id == server_id else None


class FakeWriter:
    """
    يمثل FakeWriter جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, success=True):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: success.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.success = success
        self.calls = []

    def run(self, **kwargs):
        """
        يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.calls.append(kwargs)
        return WriteCommandResult(success=self.success, exit_status=0 if self.success else 1, error=None if self.success else "failed")


class FakeEvidence:
    """
    يمثل FakeEvidence جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, states=("inactive", "active", "inactive")):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: states.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.states = list(states)

    def collect(self, **_kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى collect؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return ServiceStateObservation(state=self.states.pop(0) if self.states else "unknown")


class FakeVerifier:
    """
    يمثل FakeVerifier جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def verify_state(self, *, expected_state, **_kwargs):
        """
        يتحقق من invariant أو readiness شرطها ظاهر في الكود ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى verify_state؛ المدخلات المهمة: expected_state.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return True, {"expected": expected_state, "observed": expected_state}


def make_service(*, states=("inactive", "active", "inactive"), writer=None):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_service؛ المدخلات المهمة: states، writer.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    tables = [
        ServerModel.__table__, RemediationPlanModel.__table__, RemediationSandboxResultModel.__table__,
        RemediationApprovalModel.__table__, RemediationExecutionModel.__table__, RemediationVerificationModel.__table__,
        RemediationRollbackModel.__table__, RemediationAuditEventModel.__table__, RemediationEvidenceModel.__table__,
        SandboxValidationModel.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    server = ServerModel(id=4, name="phase6-lab", host="lab", port=22, username="monitor",
                         description="safe-remediation-test non-production dedicated lab")
    with factory() as session:
        session.add(server)
        session.commit()
    return RemediationService(
        repository=RemediationRepository(factory),
        server_repository=FakeServerRepository(server),
        write_runner=writer or FakeWriter(),
        verification_runner=FakeVerifier(),
        evidence_collector=FakeEvidence(states),
        sandbox_runtime=type("Runtime", (), {"check": lambda self: SandboxRuntimeCheck(True, "claude-native-sandbox", evidence={"test": True})})(),
    )


def make_plan(service, *, action_type="start_service"):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_plan؛ المدخلات المهمة: service، action_type.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return service.create_plan(
        plan_id="phase6-plan", investigation_id="phase6-investigation", title="Sandbox validation",
        problem_summary="Validate one dedicated lab action.",
        proposed_actions=[{"id": "phase6-action", "action_type": action_type, "target": "ai-vps-remediation-test.service", "reason": "lab only"}],
        diagnosis_claim_ids=["claim"], evidence_ids=["context"], server_id=4,
    )


def test_validation_contracts_and_invalid_target_fail_closed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_validation_contracts_and_invalid_target_fail_closed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_service()
    make_plan(service)
    result = service.validate_in_isolated_sandbox(
        plan_id="phase6-plan", target_server_id=4, target_server_name="wrong", target_service="ai-vps-remediation-test.service"
    )
    assert result.status == SandboxValidationStatus.FAILED.value
    assert "target identity" in result.failure_reason


def test_successful_validation_persists_evidence_and_allows_approval():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_successful_validation_persists_evidence_and_allows_approval؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_service()
    plan = make_plan(service)
    result = service.validate_in_isolated_sandbox(
        plan_id=plan.plan_id, target_server_id=4, target_server_name="phase6-lab", target_service="ai-vps-remediation-test.service"
    )
    assert result.status == SandboxValidationStatus.PASSED.value
    assert service.get_plan(plan.plan_id).status == "sandbox_passed"
    assert result.plan_fingerprint == plan.plan_fingerprint
    assert len(result.before_evidence_ids) == 1
    assert len(result.after_evidence_ids) == 1
    approval = service.request_approval(plan_id=plan.plan_id)
    assert approval.plan_fingerprint == plan.plan_fingerprint
    approved = service.approve(approval_id=approval.approval_id, approver="phase6-test")
    assert approved.status == "approved"
    assert service.get_plan(plan.plan_id).status == "approved"


def test_action_or_verification_failure_blocks_approval():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_action_or_verification_failure_blocks_approval؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_service(writer=FakeWriter(success=False))
    plan = make_plan(service)
    result = service.validate_in_isolated_sandbox(
        plan_id=plan.plan_id, target_server_id=4, target_server_name="phase6-lab", target_service="ai-vps-remediation-test.service"
    )
    assert result.status == SandboxValidationStatus.FAILED.value
    assert service.get_plan(plan.plan_id).status != "sandbox_passed"
    with pytest.raises(ValueError, match="must pass"):
        service.request_approval(plan_id=plan.plan_id)


def test_changed_fingerprint_marks_validation_stale_and_blocks_approval():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_changed_fingerprint_marks_validation_stale_and_blocks_approval؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_service()
    plan = make_plan(service)
    result = service.validate_in_isolated_sandbox(
        plan_id=plan.plan_id, target_server_id=4, target_server_name="phase6-lab", target_service="ai-vps-remediation-test.service"
    )
    service._repository.update_plan_status(plan.plan_id, plan.status, plan_fingerprint="changed-fingerprint")
    with pytest.raises(ValueError, match="stale"):
        service.request_approval(plan_id=plan.plan_id)
    assert service.get_sandbox_validation(result.validation_id).status == SandboxValidationStatus.STALE.value


def test_stale_successful_validation_cannot_promote_changed_plan():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_stale_successful_validation_cannot_promote_changed_plan؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_service()
    plan = make_plan(service)
    validation_id = "stale-validation"
    before = service._repository.create_evidence(
        evidence_id="stale-before", plan_id=plan.plan_id, execution_id=validation_id,
        server_id=4, service="ai-vps-remediation-test.service", phase="sandbox_before",
        observed_state="inactive", metadata={},
    )
    after = service._repository.create_evidence(
        evidence_id="stale-after", plan_id=plan.plan_id, execution_id=validation_id,
        server_id=4, service="ai-vps-remediation-test.service", phase="sandbox_after",
        observed_state="active", metadata={},
    )
    service._repository.update_plan_status(plan.plan_id, plan.status, plan_fingerprint="new-fingerprint")

    result = service._repository.finalize_sandbox_validation(
        validation_id=validation_id, plan_id=plan.plan_id, plan_fingerprint=plan.plan_fingerprint,
        server_id=4, server_name="phase6-lab", service="ai-vps-remediation-test.service",
        action_type="start_service", action_parameters={}, expected_state="active",
        observed_state="active", before_evidence_ids=[before.evidence_id],
        after_evidence_ids=[after.evidence_id], verification_status="verified", status="passed",
        started_at=datetime.now(), finished_at=datetime.now(), failure_reason=None,
        validation_metadata={"runtime": "claude-native-sandbox", "runtime_evidence": {"test": True}},
    )

    assert result.status == SandboxValidationStatus.STALE.value
    assert service.get_plan(plan.plan_id).status != "sandbox_passed"


def test_unverified_validation_cannot_promote_plan():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_unverified_validation_cannot_promote_plan؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_service()
    plan = make_plan(service)
    validation_id = "unverified-validation"
    before = service._repository.create_evidence(
        evidence_id="unverified-before", plan_id=plan.plan_id, execution_id=validation_id,
        server_id=4, service="ai-vps-remediation-test.service", phase="sandbox_before",
        observed_state="inactive", metadata={},
    )
    after = service._repository.create_evidence(
        evidence_id="unverified-after", plan_id=plan.plan_id, execution_id=validation_id,
        server_id=4, service="ai-vps-remediation-test.service", phase="sandbox_after",
        observed_state="active", metadata={},
    )

    result = service._repository.finalize_sandbox_validation(
        validation_id=validation_id, plan_id=plan.plan_id, plan_fingerprint=plan.plan_fingerprint,
        server_id=4, server_name="phase6-lab", service="ai-vps-remediation-test.service",
        action_type="start_service", action_parameters={}, expected_state="active",
        observed_state="active", before_evidence_ids=[before.evidence_id],
        after_evidence_ids=[after.evidence_id], verification_status="inconclusive", status="passed",
        started_at=datetime.now(), finished_at=datetime.now(), failure_reason=None,
        validation_metadata={"runtime": "claude-native-sandbox", "runtime_evidence": {"test": True}},
    )

    assert result.status == SandboxValidationStatus.FAILED.value
    assert service.get_plan(plan.plan_id).status != "sandbox_passed"


def test_mismatched_action_and_target_cannot_promote_plan():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_mismatched_action_and_target_cannot_promote_plan؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_service()
    plan = make_plan(service)
    validation_id = "mismatch-validation"
    before = service._repository.create_evidence(
        evidence_id="mismatch-before", plan_id=plan.plan_id, execution_id=validation_id,
        server_id=4, service="other.service", phase="sandbox_before",
        observed_state="inactive", metadata={},
    )
    after = service._repository.create_evidence(
        evidence_id="mismatch-after", plan_id=plan.plan_id, execution_id=validation_id,
        server_id=4, service="other.service", phase="sandbox_after",
        observed_state="active", metadata={},
    )

    result = service._repository.finalize_sandbox_validation(
        validation_id=validation_id, plan_id=plan.plan_id, plan_fingerprint=plan.plan_fingerprint,
        server_id=4, server_name="phase6-lab", service="other.service",
        action_type="stop_service", action_parameters={}, expected_state="active",
        observed_state="active", before_evidence_ids=[before.evidence_id],
        after_evidence_ids=[after.evidence_id], verification_status="verified", status="passed",
        started_at=datetime.now(), finished_at=datetime.now(), failure_reason=None,
        validation_metadata={"runtime": "claude-native-sandbox", "runtime_evidence": {"test": True}},
    )

    assert result.status == SandboxValidationStatus.FAILED.value
    assert service.get_plan(plan.plan_id).status != "sandbox_passed"


def test_mismatched_server_cannot_promote_plan():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_mismatched_server_cannot_promote_plan؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_service()
    plan = make_plan(service)
    validation_id = "server-mismatch-validation"
    before = service._repository.create_evidence(
        evidence_id="server-mismatch-before", plan_id=plan.plan_id, execution_id=validation_id,
        server_id=4, service="ai-vps-remediation-test.service", phase="sandbox_before",
        observed_state="inactive", metadata={},
    )
    after = service._repository.create_evidence(
        evidence_id="server-mismatch-after", plan_id=plan.plan_id, execution_id=validation_id,
        server_id=4, service="ai-vps-remediation-test.service", phase="sandbox_after",
        observed_state="active", metadata={},
    )

    result = service._repository.finalize_sandbox_validation(
        validation_id=validation_id, plan_id=plan.plan_id, plan_fingerprint=plan.plan_fingerprint,
        server_id=99, server_name="other-lab", service="ai-vps-remediation-test.service",
        action_type="start_service", action_parameters={}, expected_state="active",
        observed_state="active", before_evidence_ids=[before.evidence_id],
        after_evidence_ids=[after.evidence_id], verification_status="verified", status="passed",
        started_at=datetime.now(), finished_at=datetime.now(), failure_reason=None,
        validation_metadata={"runtime": "claude-native-sandbox", "runtime_evidence": {"test": True}},
    )

    assert result.status == SandboxValidationStatus.FAILED.value
    assert service.get_plan(plan.plan_id).status != "sandbox_passed"


def test_restart_and_reload_cannot_be_validated_without_restoration():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_restart_and_reload_cannot_be_validated_without_restoration؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    for action_type in ("restart_service", "reload_service"):
        service = make_service()
        plan = make_plan(service, action_type=action_type)
        result = service.validate_in_isolated_sandbox(
            plan_id=plan.plan_id, target_server_id=4, target_server_name="phase6-lab", target_service="ai-vps-remediation-test.service"
        )
        assert result.status == SandboxValidationStatus.FAILED.value


def test_native_sandbox_runtime_is_required_by_default():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_native_sandbox_runtime_is_required_by_default؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_service()
    service._sandbox_runtime = type("Runtime", (), {"check": lambda self: SandboxRuntimeCheck(False, "claude-native-sandbox", "attestation_missing")})()
    plan = make_plan(service)
    result = service.validate_in_isolated_sandbox(
        plan_id=plan.plan_id, target_server_id=4, target_server_name="phase6-lab", target_service="ai-vps-remediation-test.service"
    )
    assert result.status == SandboxValidationStatus.FAILED.value
    assert "native_sandbox_unavailable" in result.failure_reason
