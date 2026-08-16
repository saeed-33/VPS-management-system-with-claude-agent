"""
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


class FakeResponse:
    """
    يمثل FakeResponse جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(
        self,
        *,
        status_code=200,
        payload=None,
        text="",
    ):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: status_code، payload، text.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

        request = httpx.Request(
            "POST",
            "http://localhost:11434/api/chat",
        )

        self._response = httpx.Response(
            status_code=status_code,
            request=request,
            text=text,
        )

    def raise_for_status(self):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى raise_for_status؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self._response.raise_for_status()

    def json(self):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى json؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self._payload


class FakeHTTPClient:
    """
    يمثل FakeHTTPClient جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, responses):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: responses.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.responses = list(responses)
        self.requests = []

    async def post(self, path, json):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى post؛ المدخلات المهمة: path، json.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.requests.append((path, json))
        return self.responses.pop(0)


def valid_content():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى valid_content؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return json.dumps(
        {
            "summary": "NGINX requires live status evidence.",
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
                        "service": "nginx",
                    },
                    "rationale": "Check NGINX service state.",
                }
            ],
        }
    )


def make_client(responses):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_client؛ المدخلات المهمة: responses.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    client = OllamaSpecialistReasoningClient(
        base_url="http://localhost:11434",
        model="test-model",
        timeout_seconds=30,
    )
    fake = FakeHTTPClient(responses)
    client._client = fake
    return client, fake


def test_schema_http_400_falls_back_to_json_mode():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_schema_http_400_falls_back_to_json_mode؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client, fake = make_client(
        [
            FakeResponse(
                status_code=400,
                text="schema format unsupported",
            ),
            FakeResponse(
                payload={
                    "done": True,
                    "done_reason": "stop",
                    "message": {
                        "content": valid_content(),
                    },
                },
            ),
        ]
    )

    output = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(fake.requests) == 2
    assert isinstance(fake.requests[0][1]["format"], dict)
    assert fake.requests[1][1]["format"] == "json"
    assert (
        output.diagnostic_tool_requests[0].tool_id
        == "systemd-status"
    )


def test_bad_json_retries_once_in_json_mode():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_bad_json_retries_once_in_json_mode؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client, fake = make_client(
        [
            FakeResponse(
                payload={
                    "done": True,
                    "done_reason": "length",
                    "message": {
                        "content": '{"summary":"bad',
                    },
                },
            ),
            FakeResponse(
                payload={
                    "done": True,
                    "done_reason": "stop",
                    "message": {
                        "content": valid_content(),
                    },
                },
            ),
        ]
    )

    output = asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(fake.requests) == 2
    assert isinstance(fake.requests[0][1]["format"], dict)
    assert fake.requests[1][1]["format"] == "json"
    assert fake.requests[0][1]["options"]["num_predict"] == 6144
    assert fake.requests[1][1]["options"]["num_predict"] == 8192
    assert output.summary


def test_valid_schema_output_needs_one_request():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_valid_schema_output_needs_one_request؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client, fake = make_client(
        [
            FakeResponse(
                payload={
                    "done": True,
                    "done_reason": "stop",
                    "message": {
                        "content": valid_content(),
                    },
                },
            ),
        ]
    )

    asyncio.run(
        client.reason(
            system_prompt="system",
            user_prompt="context",
        )
    )

    assert len(fake.requests) == 1
    assert isinstance(fake.requests[0][1]["format"], dict)
