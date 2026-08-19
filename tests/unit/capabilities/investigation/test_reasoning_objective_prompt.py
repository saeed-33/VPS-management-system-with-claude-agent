"""Tests for test reasoning objective prompt.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.investigation.specialist_context، app.capabilities.investigation.specialist_reasoning_agent، app.core.contracts.specialist_reasoning.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio

from app.capabilities.investigation.specialist_context.specialist_context_snapshot import SpecialistContextSnapshot
from app.capabilities.investigation.specialist_reasoning_agent.specialist_reasoning_agent import SpecialistReasoningAgent
from app.core.contracts.specialist_reasoning.specialist_reasoning_output import SpecialistReasoningOutput


class Client:
    """
    يمثل Client جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.user_prompt = None

    async def reason(
        self,
        *,
        system_prompt,
        user_prompt,
    ):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى reason؛ المدخلات المهمة: system_prompt، user_prompt.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.user_prompt = user_prompt

        return SpecialistReasoningOutput(
            summary="Need direct NGINX evidence.",
            confidence=0.2,
        )


def context():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى context؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    objective = (
        "Determine whether NGINX is installed/running "
        "and what live evidence supports the conclusion."
    )

    return SpecialistContextSnapshot(
        task_id="task-1",
        investigation_id="inv-1",
        specialist_slug="nginx",
        specialist_name="Nginx Investigator",
        objective=objective,
        instructions=None,
        domains=("nginx", "http", "network"),
        knowledge_query="test",
        initial_analysis_summary=None,
        initial_analysis_issues=(),
        evidence=(),
        incidents=(),
        knowledge_chunks=(),
        knowledge_sources=(),
        rendered_context=(
            "## Specialist\n"
            "slug: nginx\n"
            f"objective: {objective}"
        ),
        character_count=100,
    )


def test_objective_is_prominent_before_and_after_catalog():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_objective_is_prominent_before_and_after_catalog؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client = Client()
    ctx = context()

    asyncio.run(
        SpecialistReasoningAgent(
            client=client
        ).reason(
            context=ctx,
            diagnostic_tool_catalog=(
                '[{"tool_id":"systemd-status"},'
                '{"tool_id":"network-route"}]'
            ),
        )
    )

    prompt = client.user_prompt

    assert prompt.startswith(
        "## Mandatory Investigation Objective\n"
        + ctx.objective
    )

    catalog_index = prompt.index(
        "## Available Diagnostic Tools"
    )

    reminder_index = prompt.index(
        "## Objective Reminder"
    )

    assert reminder_index > catalog_index
    assert (
        ctx.objective
        in prompt[reminder_index:]
    )
    assert (
        "The Tool catalog is capability metadata, "
        "not the problem statement."
        in prompt
    )
