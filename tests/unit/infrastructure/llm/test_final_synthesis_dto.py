"""Tests for test final synthesis dto.
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


def test_final_synthesis_minimal_contract_succeeds():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_final_synthesis_minimal_contract_succeeds؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    calls = []

    async def handler(request):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى handler؛ المدخلات المهمة: request.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        calls.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(
                        {
                            "summary": "NGINX is not confirmed running.",
                            "confidence": 0.8,
                            "missing_evidence": [
                                "Package installation evidence."
                            ],
                            "recommended_next_specialists": [
                                "systemd-service"
                            ],
                        }
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

    output = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt=(
                "context\n\n"
                "## Final Synthesis Required\n"
                "No more Tools."
            ),
        )
    )

    assert output.summary == "NGINX is not confirmed running."
    assert output.findings == []
    assert output.hypotheses == []
    assert output.diagnostic_tool_requests == []
    assert output.recommended_next_specialists == [
        "systemd-service"
    ]
    assert calls[0]["format"] == "json"
    assert calls[0]["options"]["num_ctx"] == 32768
    assert calls[0]["options"]["num_predict"] == 6144

    asyncio.run(client.close())
