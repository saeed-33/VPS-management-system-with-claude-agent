"""Tests for test specialist reasoning client.
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
import pytest

from app.infrastructure.llm.ollama.specialist_reasoning_client.client import (
    OllamaSpecialistReasoningClient,
)


VALID_OUTPUT = {
    "summary": "Concise result.",
    "confidence": 0.7,
    "findings": [],
    "hypotheses": [],
    "ruled_out": [],
    "missing_evidence": [],
    "recommended_next_specialists": [],
    "diagnostic_tool_requests": [],
}

FINAL_SYNTHESIS_OUTPUT = {
    "summary": "Concise result.",
    "confidence": 0.7,
    "missing_evidence": [],
    "recommended_next_specialists": [],
}


def make_response(status_code, payload, request):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_response؛ المدخلات المهمة: status_code، payload، request.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return httpx.Response(
        status_code,
        json=payload,
        request=request,
    )


def test_schema_rejection_is_cached_and_json_fallback_succeeds():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_schema_rejection_is_cached_and_json_fallback_succeeds؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    calls = []
    schema_rejected = False

    async def handler(request):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى handler؛ المدخلات المهمة: request.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        nonlocal schema_rejected

        body = json.loads(request.content)
        calls.append(body)

        if (
            not schema_rejected
            and body["format"] != "json"
        ):
            schema_rejected = True
            return make_response(
                400,
                {"error": "failed to parse grammar"},
                request,
            )

        return make_response(
            200,
            {
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(VALID_OUTPUT)
                },
            },
            request,
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

    parsed = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert parsed.summary == "Concise result."
    assert calls[0]["format"] != "json"
    assert calls[1]["format"] == "json"
    assert client._schema_format_supported is False

    calls.clear()

    asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(calls) == 1
    assert calls[0]["format"] == "json"

    asyncio.run(client.close())


def test_length_retry_uses_compact_retry_instruction():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_length_retry_uses_compact_retry_instruction؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
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

        if len(calls) == 1:
            return make_response(
                200,
                {
                    "done_reason": "length",
                    "message": {
                        "content": '{"summary":"truncated"'
                    },
                },
                request,
            )

        return make_response(
            200,
            {
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(VALID_OUTPUT)
                },
            },
            request,
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

    parsed = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert parsed.summary == "Concise result."
    assert len(calls) == 2

    first_prompt = calls[0]["messages"][1]["content"]
    second_prompt = calls[1]["messages"][1]["content"]

    assert "## Structured Output Contract" in first_prompt
    assert "## Retry Requirement" not in first_prompt
    assert "## Retry Requirement" in second_prompt
    assert "Prefer fewer findings" in second_prompt

    asyncio.run(client.close())

def test_final_synthesis_enables_provider_compact_mode():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_final_synthesis_enables_provider_compact_mode؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
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

        return make_response(
            200,
            {
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(FINAL_SYNTHESIS_OUTPUT)
                },
            },
            request,
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
            user_prompt=(
                "context\n\n"
                "## Final Synthesis Required\n"
                "No more Tools."
            ),
        )
    )

    prompt = calls[0]["messages"][1]["content"]

    assert "Provider Final-Synthesis Compact Mode" in prompt
    assert "Allowed keys are only: summary, confidence" in prompt
    assert "Do not output findings, hypotheses, ruled_out" in prompt
    assert calls[0]["options"]["num_predict"] == 6144
    assert calls[0]["options"]["num_ctx"] == 32768

    asyncio.run(client.close())


def test_ollama_prompt_rejects_raw_evidence_text_and_requires_exact_ids():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_ollama_prompt_rejects_raw_evidence_text_and_requires_exact_ids؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
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
        return make_response(
            200,
            {
                "done_reason": "stop",
                "message": {
                    "content": json.dumps(VALID_OUTPUT),
                },
            },
            request,
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

    asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt=(
                "Current Evidence\n"
                "evidence_id: evidence-A\n"
                "excerpt: Active: inactive (dead)\n"
                "Evidence ID Allowlist: evidence-A"
            ),
        )
    )

    prompt = calls[0]["messages"][1]["content"]
    assert "exact opaque ID token" in prompt
    assert "never put observations" in prompt
    assert "never invent or paraphrase one" in prompt

    asyncio.run(client.close())


def test_ollama_invalid_structured_result_fails_closed_after_retry():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_ollama_invalid_structured_result_fails_closed_after_retry؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
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
        return make_response(
            200,
            {
                "done_reason": "stop",
                "message": {
                    "content": '{"summary":"not complete"',
                },
            },
            request,
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

    with pytest.raises(
        RuntimeError,
        match="invalid specialist structured output",
    ):
        asyncio.run(
            client.reason(
                system_prompt="system",
                user_prompt="context",
            )
        )

    assert len(calls) == 2
    asyncio.run(client.close())


def test_ollama_normalizes_common_remediation_aliases_before_validation():
    """
    يثبت تصحيح مخرج Ollama الذي يستخدم action ويضع مرجع معرفة داخل فرضية.
    """
    calls = []
    output = json.loads(json.dumps(VALID_OUTPUT))
    output["hypotheses"] = [{
        "statement": "The service is inactive.",
        "confidence": 0.9,
        "supporting_evidence_ids": [],
        "contradicting_evidence_ids": [],
        "knowledge_source_ids": ["knowledge-chunk:1"],
    }]
    output["recommended_remediation_actions"] = [{
        "action": "start_service",
        "target": "ai-vps-remediation-test.service",
        "description": "The expected service is inactive.",
        "extra_model_field": "discarded",
    }]

    async def handler(request):
        calls.append(json.loads(request.content))
        return make_response(
            200,
            {
                "done_reason": "stop",
                "message": {"content": json.dumps(output)},
            },
            request,
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

    parsed = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(calls) == 1
    assert parsed.hypotheses[0].supporting_evidence_ids == []
    action = parsed.recommended_remediation_actions[0]
    assert action.action_type == "start_service"
    assert action.reason == "The expected service is inactive."
    assert action.expected_effect == "The named service reaches the expected state."
    asyncio.run(client.close())
