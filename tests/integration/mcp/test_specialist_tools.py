"""Tests for test specialist tools.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.contracts.investigation، app.capabilities.investigation.specialist_investigation_loop، app.capabilities.investigation.specialist_registry، app.interfaces.mcp.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio

from app.core.contracts.investigation.evidence_kind import EvidenceKind
from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.specialist_result import SpecialistResult
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus
from app.capabilities.investigation.specialist_investigation_loop.specialist_investigation_loop_result import SpecialistInvestigationLoopResult
from app.capabilities.investigation.specialist_investigation_loop.specialist_loop_stop_reason import SpecialistLoopStopReason
from app.capabilities.investigation.specialist_registry.specialist_registry_snapshot import SpecialistRegistrySnapshot
from app.capabilities.investigation.specialist_registry.specialist_runtime_definition import SpecialistRuntimeDefinition
from app.interfaces.mcp.registry import ProjectMcpToolBoundary
from app.interfaces.mcp.schemas.call import ProjectToolCall

from tests.integration.mcp.test_analysis_tools import (
    AnalysisRepository,
)
from tests.integration.mcp.test_investigation_tools import (
    ReadService,
)
from tests.integration.mcp.test_tool_boundary import (
    MonitoringService,
    ProfileService,
    ReportService,
    ServerService,
)


def specialist(
    *,
    slug="linux-cpu",
    allowed_tool_ids=("ssh.read_only",),
    max_rounds=2,
    max_actions=3,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى specialist؛ المدخلات المهمة: slug، allowed_tool_ids، max_rounds، max_actions.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SpecialistRuntimeDefinition(
        id=1,
        slug=slug,
        name="Linux CPU",
        description="CPU diagnostics",
        instructions="Investigate CPU pressure.",
        domains=("cpu",),
        trigger_hints=("high cpu",),
        knowledge_topics=("linux", "cpu"),
        allowed_tool_ids=allowed_tool_ids,
        priority=10,
        max_rounds=max_rounds,
        max_actions=max_actions,
        metadata={"owner": "admin"},
    )


class SpecialistRegistry:
    """
    يمثل SpecialistRegistry جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, definitions):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: definitions.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.definitions = tuple(definitions)

    def snapshot(self):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى snapshot؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return SpecialistRegistrySnapshot.build(
            self.definitions
        )


class SpecialistLoop:
    """
    يمثل SpecialistLoop جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.calls = []

    async def run(self, **kwargs):
        """
        يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.calls.append(kwargs)
        task = kwargs["task"]
        return SpecialistInvestigationLoopResult(
            final_result=SpecialistResult(
                task_id=task.task_id,
                specialist_id=task.specialist_id,
                status=SpecialistTaskStatus.COMPLETED,
                summary="CPU contention confirmed.",
                confidence=0.8,
                evidence_ids=("ev-1",),
            ),
            evidence=(
                EvidenceReference(
                    evidence_id="ev-1",
                    kind=EvidenceKind.COMMAND_RESULT,
                    title="top output",
                ),
            ),
            rounds_completed=1,
            actions_executed=1,
            investigation_actions_used=1,
            stop_reason=SpecialistLoopStopReason.COMPLETED,
            provider="ollama",
            model="qwen3:8b",
            traces=(),
        )


def boundary(
    *,
    registry=None,
    loop=None,
    read=None,
    analysis_repository=None,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى boundary؛ المدخلات المهمة: registry، loop، read، analysis_repository.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return ProjectMcpToolBoundary(
        server_service=ServerService(),
        monitoring_profile_service=(
            ProfileService()
        ),
        monitoring_service=MonitoringService(),
        report_query_service=ReportService(),
        analysis_repository=(
            analysis_repository
            if analysis_repository is not None
            else AnalysisRepository()
        ),
        investigation_read_service=(
            read if read is not None else ReadService()
        ),
        specialist_registry=(
            registry
            if registry is not None
            else SpecialistRegistry([specialist()])
        ),
        specialist_investigation_loop=loop,
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


def test_get_available_specialists_reads_enabled_runtime_registry():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_get_available_specialists_reads_enabled_runtime_registry؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = run_tool(
        "get_available_specialists",
        {
            "domains": ["cpu"],
        },
    )

    assert result.success is True
    assert result.data["specialists"][0]["slug"] == "linux-cpu"
    assert result.data["specialists"][0][
        "allowed_tool_ids"
    ] == ["ssh.read_only"]


def test_get_specialist_definition_reads_latest_registry_snapshot():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_get_specialist_definition_reads_latest_registry_snapshot؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    dynamic = SpecialistRegistry(
        [
            specialist(
                allowed_tool_ids=("journalctl.read",),
                max_rounds=1,
                max_actions=0,
            )
        ]
    )

    result = run_tool(
        "get_specialist_definition",
        {
            "specialist_slug": "linux-cpu",
        },
        tool_boundary=boundary(
            registry=dynamic,
        ),
    )

    assert result.success is True
    assert result.data["specialist"][
        "allowed_tool_ids"
    ] == ["journalctl.read"]
    assert result.data["specialist"]["max_actions"] == 0


def test_run_specialist_uses_selected_db_definition_and_budget():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_run_specialist_uses_selected_db_definition_and_budget؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    loop = SpecialistLoop()
    selected = specialist(
        allowed_tool_ids=("ssh.read_only", "journalctl.read"),
        max_rounds=1,
        max_actions=2,
    )

    result = run_tool(
        "run_specialist",
        {
            "investigation_id": "inv-1",
            "specialist_slug": "linux-cpu",
            "objective": "Investigate CPU pressure.",
        },
        tool_boundary=boundary(
            registry=SpecialistRegistry([selected]),
            loop=loop,
        ),
    )

    assert result.success is True
    assert result.data["result"]["provider"] == "ollama"
    assert len(loop.calls) == 1

    call = loop.calls[0]
    assert call["specialist"] is selected
    assert call["specialist"].allowed_tool_ids == (
        "ssh.read_only",
        "journalctl.read",
    )
    assert call[
        "investigation_budget"
    ].max_rounds == 3
    assert call[
        "investigation_budget"
    ].max_actions == 12
    assert call["task"].status == (
        SpecialistTaskStatus.RUNNING
    )
    assert call["task"].knowledge_topics == (
        "linux",
        "cpu",
    )
    assert call["initial_analysis_issues"] == (
        {
            "title": "High CPU",
        },
    )


def test_run_specialist_rejects_unselected_specialist():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_run_specialist_rejects_unselected_specialist؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    loop = SpecialistLoop()

    result = run_tool(
        "run_specialist",
        {
            "investigation_id": "inv-1",
            "specialist_slug": "network",
            "objective": "Investigate network.",
        },
        tool_boundary=boundary(
            registry=SpecialistRegistry(
                [
                    specialist(
                        slug="network",
                    )
                ]
            ),
            loop=loop,
        ),
    )

    assert result.success is False
    assert result.error_code == "specialist_not_selected"
    assert loop.calls == []


def test_run_specialist_requires_configured_loop():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_run_specialist_requires_configured_loop؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = run_tool(
        "run_specialist",
        {
            "investigation_id": "inv-1",
            "specialist_slug": "linux-cpu",
            "objective": "Investigate CPU pressure.",
        },
    )

    assert result.success is False
    assert result.error_code == "validation_error"
    assert (
        "specialist_investigation_loop"
        in result.error_message
    )
