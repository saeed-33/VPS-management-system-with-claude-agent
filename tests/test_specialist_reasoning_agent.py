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
from dataclasses import replace

import pytest

from app.core.contracts.investigation import (
    EvidenceKind,
    EvidenceReference,
    KnowledgeSourceReference,
    KnowledgeSourceType,
)
from app.capabilities.investigation.specialist_context import (
    SpecialistContextSnapshot,
)
from app.capabilities.investigation.specialist_reasoning_agent import (
    SpecialistReasoningAgent,
)
from app.core.contracts.specialist_reasoning import (
    SpecialistFindingOutput,
    SpecialistHypothesisOutput,
    SpecialistReasoningOutput,
)


class Client:
    """
    يمثل Client جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    provider_name = "test"
    model_name = "test-model"

    def __init__(self, output):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: output.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.output = output
        self.system_prompt = None
        self.user_prompt = None

    async def reason(self, *, system_prompt, user_prompt):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى reason؛ المدخلات المهمة: system_prompt، user_prompt.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        return self.output


class SequenceClient(Client):
    """
    يعيد مخرجات متتابعة لاختبار إعادة محاولة إصلاح provenance.
    """
    def __init__(self, outputs):
        """
        يجهز قائمة الردود وعدد الاستدعاءات.
        """
        super().__init__(outputs[0])
        self.outputs = list(outputs)
        self.calls = 0

    async def reason(self, *, system_prompt, user_prompt):
        """
        يعيد الرد التالي مع حفظ آخر prompt.
        """
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        output = self.outputs[
            min(self.calls, len(self.outputs) - 1)
        ]
        self.calls += 1
        return output


def context():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى context؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SpecialistContextSnapshot(
        task_id="task-1",
        investigation_id="inv-1",
        specialist_slug="nginx",
        specialist_name="NGINX Specialist",
        objective="Diagnose 502 errors.",
        instructions="Use supplied evidence only.",
        domains=("nginx", "proxy"),
        knowledge_query="nginx proxy 502",
        initial_analysis_summary=None,
        initial_analysis_issues=(),
        evidence=(
            EvidenceReference(
                evidence_id="evidence-A",
                kind=EvidenceKind.COMMAND_RESULT,
                title="Service status",
                excerpt="Active: inactive (dead)",
            ),
        ),
        incidents=(),
        knowledge_chunks=(),
        knowledge_sources=(
            KnowledgeSourceReference(
                source_id="knowledge-chunk:12",
                source_type=(
                    KnowledgeSourceType.OFFICIAL_DOCUMENTATION
                ),
                title="NGINX docs",
            ),
        ),
        rendered_context=(
            "[knowledge:chunk-12] proxy documentation"
        ),
        character_count=46,
    )


def valid_output():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى valid_output؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SpecialistReasoningOutput(
        summary="The current context suggests a proxy-related path.",
        confidence=0.55,
        findings=[
            SpecialistFindingOutput(
                title="Proxy module is relevant",
                description=(
                    "The supplied documentation identifies proxy support."
                ),
                confidence=0.7,
                knowledge_source_ids=["knowledge-chunk:12"],
            )
        ],
        hypotheses=[
            SpecialistHypothesisOutput(
                statement=(
                    "The 502 may originate from an unavailable upstream."
                ),
                confidence=0.45,
            )
        ],
        missing_evidence=[
            "NGINX error log around the failing request."
        ],
        recommended_next_specialists=[],
    )


def test_reasoning_converts_valid_output_to_contract():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_reasoning_converts_valid_output_to_contract؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client = Client(valid_output())
    agent = SpecialistReasoningAgent(client=client)

    execution = asyncio.run(
        agent.reason(context=context())
    )

    result = execution.result

    assert result.status.value == "completed"
    assert result.findings[0].knowledge_source_ids == (
        "knowledge-chunk:12",
    )
    assert result.missing_evidence == (
        "NGINX error log around the failing request.",
    )
    assert result.metadata["reasoning_only"] is True


def test_unknown_knowledge_citation_is_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_unknown_knowledge_citation_is_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    output = valid_output()
    output.findings[0].knowledge_source_ids = [
        "knowledge-chunk:999"
    ]

    agent = SpecialistReasoningAgent(
        client=Client(output)
    )

    with pytest.raises(
        ValueError,
        match="unknown knowledge IDs",
    ):
        asyncio.run(
            agent.reason(context=context())
        )


def test_unknown_recommended_specialist_is_dropped():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_unknown_recommended_specialist_is_dropped؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    output = valid_output()
    output.recommended_next_specialists = [
        "invented-specialist"
    ]

    agent = SpecialistReasoningAgent(
        client=Client(output)
    )

    execution = asyncio.run(
        agent.reason(
            context=context(),
            allowed_specialist_slugs=(
                "nginx",
                "linux-network",
            ),
        )
    )

    assert execution.result.recommended_next_specialists == ()
    assert execution.result.metadata[
        "dropped_specialist_recommendations"
    ] == ["invented-specialist"]


def test_systemd_alias_maps_to_systemd_service():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_systemd_alias_maps_to_systemd_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    output = valid_output()
    output.recommended_next_specialists = [
        "systemd",
        "logging",
    ]

    agent = SpecialistReasoningAgent(
        client=Client(output)
    )

    execution = asyncio.run(
        agent.reason(
            context=context(),
            allowed_specialist_slugs=(
                "nginx",
                "systemd-service",
                "linux-network",
            ),
        )
    )

    assert execution.result.recommended_next_specialists == (
        "systemd-service",
    )
    assert execution.result.metadata[
        "dropped_specialist_recommendations"
    ] == ["logging"]


def test_prompt_has_no_tool_execution_request():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_prompt_has_no_tool_execution_request؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client = Client(valid_output())
    agent = SpecialistReasoningAgent(client=client)

    asyncio.run(
        agent.reason(context=context())
    )

    assert "read-only" in client.system_prompt
    assert "performed any external action" in client.system_prompt


def test_prompt_lists_exact_evidence_id_allowlist_without_raw_observation():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_prompt_lists_exact_evidence_id_allowlist_without_raw_observation؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client = Client(valid_output())

    asyncio.run(
        SpecialistReasoningAgent(client=client).reason(
            context=context()
        )
    )

    assert "Allowed Evidence IDs: `evidence-A`" in client.user_prompt
    assert (
        "Allowed Knowledge Source IDs: `knowledge-chunk:12`"
        in client.user_prompt
    )
    assert "Never copy an Evidence title" in client.user_prompt
    assert "Active: inactive (dead)" not in client.user_prompt.split(
        "## Evidence ID Allowlist",
        1,
    )[1]


def test_raw_log_text_in_evidence_id_field_fails_closed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_raw_log_text_in_evidence_id_field_fails_closed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    output = valid_output()
    output.findings[0].evidence_ids = [
        "Active: inactive (dead)",
    ]

    with pytest.raises(ValueError, match="unknown evidence IDs"):
        asyncio.run(
            SpecialistReasoningAgent(client=Client(output)).reason(
                context=context()
            )
        )


def test_invalid_evidence_reference_is_retried_with_provenance_correction():
    """
    يثبت أن خطأ المرجع يعيد الطلب مرة واحدة دون تخمين معرف الدليل.
    """
    invalid = valid_output()
    invalid.findings[0].evidence_ids = [
        "PID 4363 monitor python3 99.4 0.6",
    ]

    recovered = valid_output()
    recovered.findings[0].evidence_ids = [
        "evidence-A",
    ]

    client = SequenceClient([invalid, recovered])

    execution = asyncio.run(
        SpecialistReasoningAgent(client=client).reason(
            context=context()
        )
    )

    assert client.calls == 2
    assert "Provenance Correction Required" in client.user_prompt
    assert execution.result.findings[0].evidence_ids == (
        "evidence-A",
    )


def test_invalid_knowledge_reference_is_retried_with_provenance_correction():
    """
    يثبت أن معرف مصدر المعرفة غير الصالح يعاد تصحيحه دون تخمين.
    """
    invalid = valid_output()
    invalid.findings[0].knowledge_source_ids = [
        "knowledge_source_id:N/A (Based on Initial Issues)",
    ]

    recovered = valid_output()
    recovered.findings[0].knowledge_source_ids = [
        "knowledge-chunk:12",
    ]

    client = SequenceClient([invalid, recovered])

    execution = asyncio.run(
        SpecialistReasoningAgent(client=client).reason(
            context=context()
        )
    )

    assert client.calls == 2
    assert execution.result.findings[0].knowledge_source_ids == (
        "knowledge-chunk:12",
    )


def test_evidence_from_another_context_fails_closed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_evidence_from_another_context_fails_closed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    output = valid_output()
    output.findings[0].evidence_ids = ["evidence-other-context"]

    with pytest.raises(ValueError, match="unknown evidence IDs"):
        asyncio.run(
            SpecialistReasoningAgent(client=Client(output)).reason(
                context=context()
            )
        )


def test_duplicate_evidence_ids_follow_existing_aggregate_deduplication():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_duplicate_evidence_ids_follow_existing_aggregate_deduplication؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    output = valid_output()
    output.findings[0].evidence_ids = [
        "evidence-A",
        "evidence-A",
    ]

    execution = asyncio.run(
        SpecialistReasoningAgent(client=Client(output)).reason(
            context=context()
        )
    )

    assert execution.result.findings[0].evidence_ids == (
        "evidence-A",
        "evidence-A",
    )
    assert execution.result.evidence_ids == ("evidence-A",)


def test_explicit_active_expectation_creates_supervised_start_action():
    """
    يثبت إنشاء اقتراح بدء خدمة عند وجود توقع active ودليل systemd inactive.
    """
    output = valid_output()
    output.findings[0].knowledge_source_ids = []
    systemd_context = replace(
        context(),
        specialist_slug="systemd-service",
        specialist_name="Systemd Service Specialist",
        objective=(
            "The ai-vps-remediation-test.service is expected to be active. "
            "Start the service if systemd reports it inactive."
        ),
        domains=("systemd", "service"),
        knowledge_sources=(),
        evidence=(
            EvidenceReference(
                evidence_id="systemd-evidence",
                kind=EvidenceKind.COMMAND_RESULT,
                title="Systemd status",
                excerpt="Active: inactive (dead)",
                metadata={
                    "tool_id": "systemd-status",
                    "command_text": (
                        "systemctl --no-pager --full status "
                        "ai-vps-remediation-test.service"
                    ),
                },
            ),
        ),
    )

    execution = asyncio.run(
        SpecialistReasoningAgent(client=Client(output)).reason(
            context=systemd_context,
        )
    )

    actions = execution.result.metadata["recommended_remediation_actions"]
    assert len(actions) == 1
    assert actions[0]["action_type"] == "start_service"
    assert actions[0]["target"] == "ai-vps-remediation-test.service"
    assert actions[0]["requires_approval"] is True
    assert actions[0]["evidence_requirements"] == ["systemd-evidence"]


def test_inactive_service_without_expected_active_state_creates_no_action():
    """
    يثبت عدم تشغيل خدمة متوقفة عمداً عند غياب الحالة المتوقعة الصريحة.
    """
    output = valid_output()
    output.findings[0].knowledge_source_ids = []
    systemd_context = replace(
        context(),
        specialist_slug="systemd-service",
        specialist_name="Systemd Service Specialist",
        objective="Investigate the current service state; it may be inactive by design.",
        domains=("systemd", "service"),
        knowledge_sources=(),
        evidence=(
            EvidenceReference(
                evidence_id="systemd-evidence",
                kind=EvidenceKind.COMMAND_RESULT,
                title="Systemd status",
                excerpt="Active: inactive (dead)",
                metadata={
                    "tool_id": "systemd-status",
                    "command_text": (
                        "systemctl --no-pager --full status "
                        "ai-vps-remediation-test.service"
                    ),
                },
            ),
        ),
    )

    execution = asyncio.run(
        SpecialistReasoningAgent(client=Client(output)).reason(
            context=systemd_context,
        )
    )

    assert execution.result.metadata["recommended_remediation_actions"] == []
