"""Tests for test specialist investigation loop.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.contracts.investigation، app.core.policies.diagnostic_policy، app.core.policies.diagnostic_tools، app.capabilities.investigation.specialist_context، app.capabilities.investigation.specialist_investigation_loop، app.capabilities.investigation.specialist_reasoning_agent.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio
from types import MappingProxyType

from app.core.contracts.investigation.evidence_kind import EvidenceKind
from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.investigation_budget import InvestigationBudget
from app.core.contracts.investigation.specialist_result import SpecialistResult
from app.core.contracts.investigation.specialist_task import SpecialistTask
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus
from app.core.policies.diagnostic_policy.diagnostic_policy_engine import DiagnosticPolicyEngine
from app.core.policies.diagnostic_tools.diagnostic_tool_call import DiagnosticToolCall
from app.core.policies.diagnostic_tools.factories import build_default_diagnostic_tool_registry
from app.capabilities.investigation.specialist_context.specialist_context_snapshot import SpecialistContextSnapshot
from app.capabilities.investigation.specialist_investigation_loop.specialist_investigation_loop import SpecialistInvestigationLoop
from app.capabilities.investigation.specialist_investigation_loop.specialist_loop_stop_reason import SpecialistLoopStopReason
from app.capabilities.investigation.specialist_reasoning_agent.specialist_diagnostic_tool_request import SpecialistDiagnosticToolRequest
from app.capabilities.investigation.specialist_reasoning_agent.specialist_reasoning_execution import SpecialistReasoningExecution
from app.capabilities.investigation.specialist_registry.specialist_runtime_definition import SpecialistRuntimeDefinition


class ContextBuilder:
    """
    يمثل ContextBuilder جزءًا من طبقة Test suite.

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

    async def build(
        self,
        *,
        task,
        specialist,
        detected_domains=(),
        evidence=(),
        initial_analysis_summary=None,
        initial_analysis_issues=(),
        incident_contexts=(),
    ):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى build؛ المدخلات المهمة: task، specialist، detected_domains، evidence، initial_analysis_summary، initial_analysis_issues.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.calls.append(
            tuple(
                item.evidence_id
                for item in evidence
            )
        )

        return SpecialistContextSnapshot(
            task_id=task.task_id,
            investigation_id=(
                task.investigation_id
            ),
            specialist_slug=(
                specialist.slug
            ),
            specialist_name=(
                specialist.name
            ),
            objective=task.objective,
            instructions=None,
            domains=(
                detected_domains
                or specialist.domains
            ),
            knowledge_query="test",
            initial_analysis_summary=(
                initial_analysis_summary
            ),
            initial_analysis_issues=(
                initial_analysis_issues
            ),
            evidence=tuple(evidence),
            incidents=(),
            knowledge_chunks=(),
            knowledge_sources=(),
            rendered_context="context",
            character_count=7,
        )


class ReasoningAgent:
    """
    يمثل ReasoningAgent جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, executions):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: executions.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.executions = list(
            executions
        )
        self.catalogs = []

    async def reason(
        self,
        *,
        context,
        allowed_specialist_slugs=(),
        diagnostic_tool_catalog=None,
        force_final_synthesis=False,
    ):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى reason؛ المدخلات المهمة: context، allowed_specialist_slugs، diagnostic_tool_catalog، force_final_synthesis.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.catalogs.append(
            diagnostic_tool_catalog
        )
        return self.executions.pop(0)


class EvidenceCollector:
    """
    يمثل EvidenceCollector جزءًا من طبقة Test suite.

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

    async def collect(self, request):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى collect؛ المدخلات المهمة: request.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.calls.append(request)

        return EvidenceReference(
            evidence_id=request.evidence_id,
            kind=(
                EvidenceKind.COMMAND_RESULT
            ),
            title=(
                "Collected "
                + request.policy_result.tool_id
            ),
            source_id=request.server_id,
            excerpt="live evidence",
            metadata={
                "success": True,
            },
        )


def specialist(
    *,
    allowed_tool_ids=(
        "network-listeners",
        "systemd-status",
    ),
    max_rounds=3,
    max_actions=4,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى specialist؛ المدخلات المهمة: allowed_tool_ids، max_rounds، max_actions.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SpecialistRuntimeDefinition(
        id=1,
        slug="nginx",
        name="Nginx Investigator",
        description=None,
        instructions=None,
        domains=("nginx", "network"),
        trigger_hints=(),
        knowledge_topics=(),
        allowed_tool_ids=(
            allowed_tool_ids
        ),
        priority=10,
        max_rounds=max_rounds,
        max_actions=max_actions,
        metadata=MappingProxyType({}),
    )


def task():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى task؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SpecialistTask(
        task_id="task-1",
        investigation_id="inv-1",
        server_id=2,
        report_id=1,
        specialist_id="nginx",
        objective="Investigate NGINX.",
    )


def result(
    *,
    summary,
    confidence,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى result؛ المدخلات المهمة: summary، confidence.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SpecialistResult(
        task_id="task-1",
        specialist_id="nginx",
        status=(
            SpecialistTaskStatus.COMPLETED
        ),
        summary=summary,
        confidence=confidence,
    )


def execution(
    *,
    summary,
    confidence,
    requests=(),
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى execution؛ المدخلات المهمة: summary، confidence، requests.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SpecialistReasoningExecution(
        result=result(
            summary=summary,
            confidence=confidence,
        ),
        provider="fake",
        model="fake-model",
        diagnostic_tool_requests=tuple(
            requests
        ),
    )


def request_tool(
    tool_id,
    arguments,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى request_tool؛ المدخلات المهمة: tool_id، arguments.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SpecialistDiagnosticToolRequest(
        call=DiagnosticToolCall(
            tool_id=tool_id,
            arguments=arguments,
        ),
        rationale="Need live evidence.",
    )


def make_loop(executions):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_loop؛ المدخلات المهمة: executions.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    context_builder = ContextBuilder()
    reasoning_agent = ReasoningAgent(
        executions
    )
    collector = EvidenceCollector()
    registry = (
        build_default_diagnostic_tool_registry()
    )

    loop = SpecialistInvestigationLoop(
        context_builder=context_builder,
        reasoning_agent=reasoning_agent,
        diagnostic_tool_registry=registry,
        diagnostic_policy_engine=(
            DiagnosticPolicyEngine(
                registry=registry
            )
        ),
        evidence_collection_service=(
            collector
        ),
    )

    return (
        loop,
        context_builder,
        reasoning_agent,
        collector,
    )


def test_loop_collects_evidence_then_reasons_again():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_loop_collects_evidence_then_reasons_again؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    first = execution(
        summary="Need listeners.",
        confidence=0.2,
        requests=(
            request_tool(
                "network-listeners",
                {},
            ),
        ),
    )

    second = execution(
        summary="Listener evidence reviewed.",
        confidence=0.8,
        requests=(),
    )

    loop, context_builder, agent, collector = (
        make_loop(
            [first, second]
        )
    )

    output = asyncio.run(
        loop.run(
            task=task(),
            specialist=specialist(),
            investigation_budget=(
                InvestigationBudget(
                    max_specialists=4,
                    max_rounds=3,
                    max_actions=12,
                )
            ),
        )
    )

    assert output.stop_reason == (
        SpecialistLoopStopReason.COMPLETED
    )
    assert output.rounds_completed == 2
    assert output.actions_executed == 1
    assert len(output.evidence) == 1
    assert len(output.final_result.findings) == 1
    assert output.final_result.evidence_ids == (
        "task-1:r1:a1:network-listeners",
    )
    assert collector.calls
    assert context_builder.calls == [
        (),
        (
            "task-1:r1:a1:"
            "network-listeners",
        ),
    ]
    assert "network-listeners" in (
        agent.catalogs[0]
    )


def test_denied_request_forces_synthesis_without_execution():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_denied_request_forces_synthesis_without_execution؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    first = execution(
        summary="Need an unassigned tool.",
        confidence=0.1,
        requests=(
            request_tool(
                "postgres-ready",
                {},
            ),
        ),
    )

    second = execution(
        summary=(
            "Final conclusion from existing evidence; "
            "the requested Tool was unavailable."
        ),
        confidence=0.3,
        requests=(),
    )

    loop, _, _, collector = (
        make_loop([first, second])
    )

    output = asyncio.run(
        loop.run(
            task=task(),
            specialist=specialist(
                allowed_tool_ids=(
                    "network-listeners",
                )
            ),
            investigation_budget=(
                InvestigationBudget()
            ),
        )
    )

    assert output.stop_reason == (
        SpecialistLoopStopReason.COMPLETED
    )
    assert output.rounds_completed == 2
    assert output.actions_executed == 0
    assert collector.calls == []
    assert (
        output
        .traces[0]
        .tool_decisions[0]
        .decision
        == "denied"
    )
    assert output.final_result.summary == (
        "Final conclusion from existing evidence; "
        "the requested Tool was unavailable."
    )


def test_last_round_requests_are_not_executed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_last_round_requests_are_not_executed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    first = execution(
        summary="Still need evidence.",
        confidence=0.2,
        requests=(
            request_tool(
                "network-listeners",
                {},
            ),
        ),
    )

    synthesis = execution(
        summary=(
            "Final synthesis at the round boundary."
        ),
        confidence=0.4,
        requests=(),
    )

    loop, context_builder, agent, collector = (
        make_loop([first, synthesis])
    )

    output = asyncio.run(
        loop.run(
            task=task(),
            specialist=specialist(
                max_rounds=1
            ),
            investigation_budget=(
                InvestigationBudget(
                    max_rounds=1
                )
            ),
        )
    )

    assert output.stop_reason == (
        SpecialistLoopStopReason
        .MAX_ROUNDS
    )
    assert output.rounds_completed == 1
    assert output.actions_executed == 0
    assert collector.calls == []
    assert output.final_result.summary == (
        "Final synthesis at the round boundary."
    )
    assert context_builder.calls == [(), ()]
    assert agent.catalogs[0] is not None
    assert agent.catalogs[1] is None


def test_action_budget_stops_additional_execution():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_action_budget_stops_additional_execution؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    first = execution(
        summary="Need two checks.",
        confidence=0.2,
        requests=(
            request_tool(
                "network-listeners",
                {},
            ),
            request_tool(
                "systemd-status",
                {"service": "nginx"},
            ),
        ),
    )

    synthesis = execution(
        summary=(
            "Final synthesis from evidence collected "
            "before the action budget was exhausted."
        ),
        confidence=0.6,
        requests=(),
    )

    loop, context_builder, agent, collector = (
        make_loop([first, synthesis])
    )

    output = asyncio.run(
        loop.run(
            task=task(),
            specialist=specialist(
                max_actions=1,
            ),
            investigation_budget=(
                InvestigationBudget(
                    max_rounds=3,
                    max_actions=1,
                )
            ),
        )
    )

    assert output.stop_reason == (
        SpecialistLoopStopReason
        .MAX_ACTIONS
    )
    assert output.rounds_completed == 1
    assert output.actions_executed == 1
    assert len(collector.calls) == 1
    assert len(output.evidence) == 1
    assert output.final_result.summary == (
        "Final synthesis from evidence collected "
        "before the action budget was exhausted."
    )
    assert context_builder.calls == [
        (),
        (
            "task-1:r1:a1:"
            "network-listeners",
        ),
    ]
    assert agent.catalogs[0] is not None
    assert agent.catalogs[1] is None


def test_duplicate_request_is_not_executed_twice():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_duplicate_request_is_not_executed_twice؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    first = execution(
        summary="Need listeners.",
        confidence=0.2,
        requests=(
            request_tool(
                "network-listeners",
                {},
            ),
        ),
    )

    second = execution(
        summary="Requesting same evidence again.",
        confidence=0.3,
        requests=(
            request_tool(
                "network-listeners",
                {},
            ),
        ),
    )

    third = execution(
        summary="Final conclusion from existing evidence.",
        confidence=0.8,
        requests=(),
    )

    loop, _, _, collector = (
        make_loop(
            [first, second, third]
        )
    )

    output = asyncio.run(
        loop.run(
            task=task(),
            specialist=specialist(),
            investigation_budget=(
                InvestigationBudget()
            ),
        )
    )

    assert output.stop_reason == (
        SpecialistLoopStopReason.COMPLETED
    )
    assert output.rounds_completed == 3
    assert output.actions_executed == 1
    assert len(collector.calls) == 1
    assert (
        output
        .traces[1]
        .tool_decisions[0]
        .reasons
        == ("duplicate_request",)
    )
    assert output.final_result.summary == (
        "Final conclusion from existing evidence."
    )
