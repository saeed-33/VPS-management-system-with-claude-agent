"""Tests for test remediation tools.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.interfaces.mcp، app.infrastructure.database.models.remediation، app.infrastructure.database.repositories.remediation_repository، app.capabilities.remediation.service.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.interfaces.mcp.registry import ProjectMcpToolBoundary
from app.interfaces.mcp.schemas.call import ProjectToolCall
from app.infrastructure.database.models.remediation.plan import RemediationPlanModel
from app.infrastructure.database.models.remediation.sandbox_result import RemediationSandboxResultModel
from app.infrastructure.database.repositories.remediation_repository.repository import RemediationRepository
from app.capabilities.remediation.service.service import RemediationService

from tests.integration.mcp.test_tool_boundary import (
    MonitoringService,
    ProfileService,
    ReportService,
    ServerService,
)


def make_remediation_service(
    *,
    automatic_remediation_allowed=False,
):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_remediation_service؛ المدخلات المهمة: automatic_remediation_allowed.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )
    RemediationPlanModel.__table__.create(
        engine
    )
    RemediationSandboxResultModel.__table__.create(
        engine
    )
    factory = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
    repository = RemediationRepository(
        factory
    )
    return RemediationService(
        repository=repository,
        automatic_remediation_allowed=(
            automatic_remediation_allowed
        ),
    )


def boundary(
    *,
    remediation_service=None,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى boundary؛ المدخلات المهمة: remediation_service.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return ProjectMcpToolBoundary(
        server_service=ServerService(),
        monitoring_profile_service=(
            ProfileService()
        ),
        monitoring_service=MonitoringService(),
        report_query_service=ReportService(),
        remediation_service=(
            remediation_service
            if remediation_service is not None
            else make_remediation_service()
        ),
    )


def run_tool(
    tool_id,
    arguments,
    *,
    tool_boundary=None,
):
    """
    ينفذ مرحلة الأداة أو يحفظ نتيجة التقييم ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى run_tool؛ المدخلات المهمة: tool_id، arguments، tool_boundary.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return asyncio.run(
        (
            tool_boundary
            if tool_boundary is not None
            else boundary()
        ).execute(
            ProjectToolCall(
                tool_id=tool_id,
                arguments=arguments,
            )
        )
    )


def plan_arguments(
    *,
    plan_id="plan-1",
    risk_level="medium",
    action=None,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى plan_arguments؛ المدخلات المهمة: plan_id، risk_level، action.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return {
        "plan_id": plan_id,
        "investigation_id": "inv-1",
        "title": "Restart overloaded service",
        "problem_summary": "Service is wedged.",
        "proposed_actions": [
            action
            if action is not None
            else {
                "id": "restart-service",
                "description": (
                    "Restart service in sandbox."
                ),
                "sandbox_supported": True,
            }
        ],
        "diagnosis_claim_ids": ["claim-1"],
        "evidence_ids": ["ev-1"],
        "risk_level": risk_level,
        "rollback_plan": (
            "Restore previous service state."
        ),
    }


def test_propose_remediation_requires_diagnosis_and_evidence_links():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_propose_remediation_requires_diagnosis_and_evidence_links؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = run_tool(
        "propose_remediation",
        {
            "investigation_id": "inv-1",
            "problem_summary": "Service issue.",
            "diagnosis_claim_ids": ["claim-1"],
            "evidence_ids": ["ev-1"],
        },
    )

    assert result.success is True
    assert result.data["proposal"][
        "production_application_allowed"
    ] is False


def test_create_plan_and_sandbox_result_are_persisted():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_create_plan_and_sandbox_result_are_persisted؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_remediation_service()
    tool_boundary = boundary(
        remediation_service=service
    )

    plan = run_tool(
        "create_remediation_plan",
        plan_arguments(),
        tool_boundary=tool_boundary,
    )
    sandbox = run_tool(
        "test_remediation_in_sandbox",
        {
            "plan_id": "plan-1",
        },
        tool_boundary=tool_boundary,
    )
    latest = run_tool(
        "get_sandbox_result",
        {
            "plan_id": "plan-1",
        },
        tool_boundary=tool_boundary,
    )

    assert plan.success is True
    assert plan.data["plan"]["status"] == "proposed"
    assert sandbox.success is True
    assert sandbox.data["sandbox_result"][
        "status"
    ] == "passed"
    assert latest.success is True
    assert latest.data["sandbox_result"][
        "plan_id"
    ] == "plan-1"


def test_failed_sandbox_blocks_production_application():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_failed_sandbox_blocks_production_application؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_remediation_service()
    tool_boundary = boundary(
        remediation_service=service
    )
    run_tool(
        "create_remediation_plan",
        plan_arguments(
            action={
                "id": "dangerous-action",
                "description": "Unsupported action.",
                "sandbox_supported": False,
            }
        ),
        tool_boundary=tool_boundary,
    )
    run_tool(
        "test_remediation_in_sandbox",
        {
            "plan_id": "plan-1",
        },
        tool_boundary=tool_boundary,
    )

    result = run_tool(
        "apply_approved_remediation",
        {
            "plan_id": "plan-1",
        },
        tool_boundary=tool_boundary,
    )

    assert result.success is False
    assert result.error_code == "sandbox_failed"


def test_high_risk_action_requests_user_approval():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_high_risk_action_requests_user_approval؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_remediation_service()
    tool_boundary = boundary(
        remediation_service=service
    )
    run_tool(
        "create_remediation_plan",
        plan_arguments(
            risk_level="high",
        ),
        tool_boundary=tool_boundary,
    )
    run_tool(
        "test_remediation_in_sandbox",
        {
            "plan_id": "plan-1",
        },
        tool_boundary=tool_boundary,
    )

    result = run_tool(
        "apply_approved_remediation",
        {
            "plan_id": "plan-1",
        },
        tool_boundary=tool_boundary,
    )

    assert result.success is False
    assert result.error_code == "approval_required"


def test_policy_denied_action_cannot_be_applied_even_after_sandbox():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_policy_denied_action_cannot_be_applied_even_after_sandbox؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = make_remediation_service(
        automatic_remediation_allowed=False
    )
    tool_boundary = boundary(
        remediation_service=service
    )
    run_tool(
        "create_remediation_plan",
        plan_arguments(),
        tool_boundary=tool_boundary,
    )
    run_tool(
        "test_remediation_in_sandbox",
        {
            "plan_id": "plan-1",
        },
        tool_boundary=tool_boundary,
    )

    result = run_tool(
        "apply_approved_remediation",
        {
            "plan_id": "plan-1",
            "approved_by": "operator",
        },
        tool_boundary=tool_boundary,
    )

    assert result.success is False
    assert result.error_code == "policy_denied"
