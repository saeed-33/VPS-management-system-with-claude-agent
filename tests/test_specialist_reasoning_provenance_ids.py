"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.contracts.investigation، app.capabilities.investigation.specialist_context، app.capabilities.investigation.specialist_reasoning_agent، app.core.contracts.specialist_reasoning.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio

from app.core.contracts.investigation import (
    EvidenceKind,
    EvidenceReference,
)
from app.capabilities.investigation.specialist_context import (
    SpecialistContextSnapshot,
)
from app.capabilities.investigation.specialist_reasoning_agent import (
    SpecialistReasoningAgent,
)
from app.core.contracts.specialist_reasoning import (
    SpecialistReasoningOutput,
)


class Client:
    """
    يمثل Client جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self, output):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: output.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.output = output

    async def reason(self, *, system_prompt, user_prompt):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى reason؛ المدخلات المهمة: system_prompt، user_prompt.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.output


def context():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى context؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    evidence = EvidenceReference(
        evidence_id="analysis:638:issue:1",
        kind=EvidenceKind.ANALYSIS,
        title="Connection failure",
        source_id=638,
        excerpt="Connect call failed.",
    )

    return SpecialistContextSnapshot(
        task_id="task-1",
        investigation_id="inv-1",
        specialist_slug="linux-network",
        specialist_name="Linux Network",
        objective="Investigate connectivity.",
        instructions=None,
        domains=("network",),
        knowledge_query="test",
        initial_analysis_summary=None,
        initial_analysis_issues=(),
        evidence=(evidence,),
        incidents=(),
        knowledge_chunks=(),
        knowledge_sources=(),
        rendered_context=(
            "[evidence]\n"
            "evidence_id: analysis:638:issue:1\n"
            "excerpt: Connect call failed."
        ),
        character_count=100,
    )


def test_evidence_namespace_prefix_is_normalized_only_for_real_id():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_evidence_namespace_prefix_is_normalized_only_for_real_id؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    output = SpecialistReasoningOutput(
        summary="Connection evidence exists.",
        confidence=0.8,
        findings=[
            {
                "title": "Connection failed",
                "description": "SSH connection failed.",
                "confidence": 0.9,
                "evidence_ids": [
                    "evidence:analysis:638:issue:1"
                ],
                "knowledge_source_ids": [],
            }
        ],
    )

    execution = asyncio.run(
        SpecialistReasoningAgent(
            client=Client(output)
        ).reason(
            context=context(),
        )
    )

    assert execution.result.findings[0].evidence_ids == (
        "analysis:638:issue:1",
    )


def test_unknown_prefixed_reference_remains_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_unknown_prefixed_reference_remains_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    output = SpecialistReasoningOutput(
        summary="Bad citation.",
        confidence=0.2,
        findings=[
            {
                "title": "Bad",
                "description": "Bad citation.",
                "confidence": 0.2,
                "evidence_ids": [
                    "evidence:not-a-real-id"
                ],
                "knowledge_source_ids": [],
            }
        ],
    )

    try:
        asyncio.run(
            SpecialistReasoningAgent(
                client=Client(output)
            ).reason(
                context=context(),
            )
        )
    except ValueError as exc:
        assert "unknown evidence IDs" in str(exc)
    else:
        raise AssertionError(
            "Unknown reference should fail closed."
        )
