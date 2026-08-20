"""Tests for test context window.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.infrastructure.llm.ollama.specialist_reasoning_client.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio
import json

import httpx

from app.infrastructure.llm.ollama.specialist_reasoning_client.client import (
    OllamaSpecialistReasoningClient,
)


VALID = {
    "summary": "Concise result.",
    "confidence": 0.5,
    "findings": [],
    "hypotheses": [],
    "ruled_out": [],
    "missing_evidence": [],
    "recommended_next_specialists": [],
    "diagnostic_tool_requests": [],
}

FINAL_SYNTHESIS_VALID = {
    "summary": "Concise result.",
    "confidence": 0.5,
    "missing_evidence": [],
    "recommended_next_specialists": [],
}


def run_request(user_prompt):
    """
    ينفذ مرحلة الأداة أو يحفظ نتيجة التقييم ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى run_request؛ المدخلات المهمة: user_prompt.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    calls = []

    async def handler(request):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى handler؛ المدخلات المهمة: request.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        body = json.loads(request.content)
        calls.append(body)
        return httpx.Response(
            200,
            json={
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(
                        (
                            FINAL_SYNTHESIS_VALID
                            if "## Final Synthesis Required"
                            in user_prompt
                            else VALID
                        )
                    )
                },
            },
            request=request,
        )

    client = OllamaSpecialistReasoningClient(
        base_url="http://ollama.test",
        model="test-model",
        timeout_seconds=10,
    )
    client._schema_format_supported = False
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="http://ollama.test",
    )

    asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt=user_prompt,
        )
    )
    asyncio.run(client.close())
    return calls[0]


def test_normal_reasoning_uses_32k_context_and_6144_output():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_normal_reasoning_uses_32k_context_and_6144_output؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    payload = run_request("normal context")

    assert payload["options"]["num_ctx"] == 32768
    assert payload["options"]["num_predict"] == 6144


def test_final_synthesis_uses_32k_context_and_6144_output():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_final_synthesis_uses_32k_context_and_6144_output؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    payload = run_request(
        "context\n\n"
        "## Final Synthesis Required\n"
        "No more diagnostic execution."
    )

    assert payload["options"]["num_ctx"] == 32768
    assert payload["options"]["num_predict"] == 6144
    assert payload["format"] == "json"
