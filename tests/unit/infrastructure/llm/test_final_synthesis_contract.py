"""Tests for test final synthesis contract.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.investigation.specialist_reasoning_client.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio
import json

import httpx

from app.capabilities.investigation.specialist_reasoning_client import (
    OllamaSpecialistReasoningClient,
)


def test_final_synthesis_uses_minimal_json_mode():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_final_synthesis_uses_minimal_json_mode؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
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
                        {
                            "summary": "NGINX is not confirmed running.",
                            "confidence": 0.7,
                            "missing_evidence": [
                                "Direct process evidence."
                            ],
                            "recommended_next_specialists": [],
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
                "No more diagnostic execution."
            ),
        )
    )

    assert output.summary == "NGINX is not confirmed running."
    assert len(calls) == 1
    assert calls[0]["format"] == "json"
    assert calls[0]["options"]["num_predict"] == 6144
    assert calls[0]["options"]["num_ctx"] == 32768

    prompt = calls[0]["messages"][1]["content"]

    assert '"summary":"short conclusion"' in prompt
    assert '"hypotheses":[' not in prompt.split(
        "## Structured Output Contract",
        1,
    )[1].split("JSON rules:", 1)[0]

    asyncio.run(client.close())


def test_normal_reasoning_keeps_existing_generation_limits():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_normal_reasoning_keeps_existing_generation_limits؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
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
                        {
                            "summary": "Need evidence.",
                            "confidence": 0.2,
                            "findings": [],
                            "hypotheses": [],
                            "ruled_out": [],
                            "missing_evidence": [],
                            "recommended_next_specialists": [],
                            "diagnostic_tool_requests": [],
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

    asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="normal context",
        )
    )

    assert calls[0]["options"]["num_predict"] == 6144
    asyncio.run(client.close())
