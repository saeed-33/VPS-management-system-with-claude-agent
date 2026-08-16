"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.interfaces.admin.api.investigations، app.interfaces.admin.dependencies، app.core.contracts.investigation_read_models.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interfaces.admin.api.investigations import router
from app.interfaces.admin.dependencies import get_investigation_read_service
from app.core.contracts.investigation_read_models import (
    InvestigationCandidateReadModel,
    InvestigationDetailReadModel,
    InvestigationRuntimeReadModel,
    InvestigationSummaryReadModel,
)


NOW = datetime(2026, 8, 10, tzinfo=timezone.utc)


def summary():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى summary؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return InvestigationSummaryReadModel(
        investigation_id="inv-1",
        server_id=2,
        report_id=1076,
        analysis_id=907,
        status="completed",
        should_investigate=True,
        detected_domains=("nginx", "network"),
        selected_specialists=("nginx", "systemd-service"),
        max_specialists=2,
        max_rounds=3,
        max_actions=10,
        runtime_available=True,
        final_diagnosis_available=True,
        created_at=NOW,
        updated_at=NOW,
    )


def detail():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى detail؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return InvestigationDetailReadModel(
        investigation_id="inv-1",
        server_id=2,
        report_id=1076,
        analysis_id=907,
        status="completed",
        should_investigate=True,
        routing_reasons=("actionable_issue",),
        detected_domains=("nginx", "network"),
        unmatched_issue_indexes=(),
        registry_size=8,
        candidate_limit=12,
        selection_limit=4,
        max_specialists=2,
        max_rounds=3,
        max_actions=10,
        routing_version="deterministic-v1",
        candidates=(
            InvestigationCandidateReadModel(
                specialist_definition_id=1,
                specialist_slug="nginx",
                specialist_name="NGINX Specialist",
                score=5,
                priority=100,
                candidate_rank=1,
                is_selected=True,
                selected_rank=1,
                matched_domains=("nginx",),
            ),
        ),
        runtime_available=True,
        final_diagnosis_available=True,
        runtime=InvestigationRuntimeReadModel(
            status="completed",
            orchestrator="claude",
            execution_mode="dynamic-secondary",
            waves_completed=2,
            actions_used=4,
            evidence_count=2,
            specialist_runs=(
                {"specialist_slug": "nginx", "status": "completed"},
            ),
            evidence=({"evidence_id": "e1"},),
            correlated_claims=(
                {
                    "claim_id": "c1",
                    "certainty": "unknown",
                    "metadata": {
                        "code_locations": [{
                            "file_path": "/srv/app/main.py",
                            "line_number": 42,
                            "reason": "ValueError: invalid payload",
                            "evidence_ids": ["e1"],
                        }],
                    },
                },
            ),
            conflicts=({"conflict_id": "conflict-1"},),
            final_diagnosis={"summary": "One conflict."},
            narrative={
                "summary": "Operator narrative.",
                "used_fallback": False,
            },
        ),
        metadata={"runtime_snapshot_version": "4.19.2-v1"},
        created_at=NOW,
        updated_at=NOW,
    )


class Service:
    """
    يمثل Service جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.list_calls = []
        self.report_calls = []
        self.missing = False

    def list_recent(self, *, limit, server_id=None):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_recent؛ المدخلات المهمة: limit، server_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.list_calls.append((limit, server_id))
        return (summary(),)

    def get(self, investigation_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get؛ المدخلات المهمة: investigation_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        if self.missing:
            return None
        return detail()

    def list_by_report_id(self, report_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_by_report_id؛ المدخلات المهمة: report_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.report_calls.append(report_id)
        return (summary(),)


def make_client():
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_client؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    app = FastAPI()
    app.include_router(router)
    service = Service()
    app.dependency_overrides[
        get_investigation_read_service
    ] = lambda: service
    return TestClient(app), service


def test_list_investigations():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_list_investigations؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client, service = make_client()

    response = client.get(
        "/api/investigations",
        params={"limit": 25, "server_id": 2},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["investigation_id"] == "inv-1"
    assert payload[0]["runtime_available"] is True
    assert service.list_calls == [(25, 2)]


def test_get_investigation_includes_runtime():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_get_investigation_includes_runtime؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client, _ = make_client()

    response = client.get("/api/investigations/inv-1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime"]["orchestrator"] == "claude"
    assert (
        payload["runtime"]["final_diagnosis"]["summary"]
        == "One conflict."
    )
    assert payload["runtime"]["narrative"]["used_fallback"] is False
    location = payload["runtime"]["correlated_claims"][0]["metadata"]["code_locations"][0]
    assert location["file_path"] == "/srv/app/main.py"
    assert location["evidence_ids"] == ["e1"]


def test_get_missing_investigation_returns_404():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_get_missing_investigation_returns_404؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client, service = make_client()
    service.missing = True

    response = client.get("/api/investigations/missing")

    assert response.status_code == 404
    assert "Investigation not found" in response.json()["detail"]


def test_list_report_investigations():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_list_report_investigations؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client, service = make_client()

    response = client.get("/api/reports/1076/investigations")

    assert response.status_code == 200
    assert service.report_calls == [1076]
    assert response.json()[0]["report_id"] == 1076


def test_list_limit_validation():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_list_limit_validation؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    client, _ = make_client()

    response = client.get(
        "/api/investigations",
        params={"limit": 501},
    )

    assert response.status_code == 422
