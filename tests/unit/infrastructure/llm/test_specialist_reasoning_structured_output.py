"""Tests for test specialist reasoning structured output.
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

from app.capabilities.investigation.specialist_reasoning_client import (
    OllamaSpecialistReasoningClient,
)


class Response:
    """
    يمثل Response جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, payload):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: payload.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self._payload = payload

    def raise_for_status(self):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى raise_for_status؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return None

    def json(self):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى json؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self._payload


class HTTPClient:
    """
    يمثل HTTPClient جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, payloads):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: payloads.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.payloads = list(payloads)
        self.requests = []

    async def post(self, path, json):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى post؛ المدخلات المهمة: path، json.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.requests.append((path, json))
        return Response(self.payloads.pop(0))


def valid_content():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى valid_content؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return json.dumps(
        {
            "summary": "NGINX state requires live evidence.",
            "confidence": 0.3,
            "findings": [],
            "hypotheses": [],
            "ruled_out": [],
            "missing_evidence": [
                "Current NGINX service status."
            ],
            "recommended_next_specialists": [],
            "diagnostic_tool_requests": [
                {
                    "tool_id": "systemd-status",
                    "arguments": {
                        "service": "nginx"
                    },
                    "rationale": "Check current service state."
                }
            ],
        }
    )


def make_client(payloads):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_client؛ المدخلات المهمة: payloads.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    client = OllamaSpecialistReasoningClient(
        base_url="http://localhost:11434",
        model="test-model",
        timeout_seconds=30,
    )
    fake = HTTPClient(payloads)
    client._client = fake
    return client, fake


def test_ollama_uses_json_schema_as_format():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_ollama_uses_json_schema_as_format؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client, fake = make_client(
        [
            {
                "done": True,
                "done_reason": "stop",
                "message": {
                    "content": valid_content()
                },
            }
        ]
    )

    output = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    payload = fake.requests[0][1]

    assert isinstance(payload["format"], dict)
    assert payload["format"]["type"] == "object"
    assert output.confidence == 0.3


def test_ollama_retries_once_after_invalid_json():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_ollama_retries_once_after_invalid_json؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client, fake = make_client(
        [
            {
                "done": True,
                "done_reason": "length",
                "message": {
                    "content": "{\"summary\":\"unterminated"
                },
            },
            {
                "done": True,
                "done_reason": "stop",
                "message": {
                    "content": valid_content()
                },
            },
        ]
    )

    output = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(fake.requests) == 2
    assert fake.requests[0][1]["options"]["num_predict"] == 6144
    assert fake.requests[1][1]["options"]["num_predict"] == 8192
    assert output.summary


def test_ollama_valid_output_does_not_retry():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_ollama_valid_output_does_not_retry؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client, fake = make_client(
        [
            {
                "done": True,
                "done_reason": "stop",
                "message": {
                    "content": valid_content()
                },
            }
        ]
    )

    asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(fake.requests) == 1
