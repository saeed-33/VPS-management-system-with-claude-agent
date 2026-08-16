"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.remediation.autonomous_authorization_service، app.core.contracts.autonomous_remediation.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from datetime import datetime, timedelta, timezone

from app.capabilities.remediation.autonomous_authorization_service import AutonomousAuthorizationService
from app.core.contracts.autonomous_remediation import AutonomousDecisionOutcome, AutonomousPolicyDecision, AutonomousAuthorizationStatus


class Repository:
    """
    يمثل Repository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.authorization = None

    def create_authorization(self, authorization):
        """
        يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى create_authorization؛ المدخلات المهمة: authorization.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.authorization = authorization

    def get_authorization(self, authorization_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_authorization؛ المدخلات المهمة: authorization_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.authorization

    def consume_authorization(self, authorization_id, *, now):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى consume_authorization؛ المدخلات المهمة: authorization_id، now.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.authorization = type("Consumed", (), {"consumed_at": now})()
        return self.authorization


def test_consumption_returns_consumed_contract_for_execution_defense_in_depth():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_consumption_returns_consumed_contract_for_execution_defense_in_depth؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repository = Repository()
    service = AutonomousAuthorizationService(repository=repository)
    now = datetime.now(timezone.utc)
    decision = AutonomousPolicyDecision(
        decision_id="d1", outcome=AutonomousDecisionOutcome.AUTO_EXECUTE,
        reason_codes=("policy_match",), human_readable_reasons=("ok",),
        policy_id="p1", policy_version=1, plan_id="plan", plan_fingerprint="fp",
        server_id=4, action_type="start_service", target="nginx", evaluated_at=now,
    )
    issued = service.issue(decision=decision, sandbox_validation_id="sv1")

    class Model:
        """
        يمثل Model جزءًا من طبقة Test suite.

        يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
        تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
        """
        authorization_id = issued.authorization_id
        token = issued.token
        status = "consumed"
        policy_id = issued.policy_id
        policy_version = issued.policy_version
        decision_id = issued.decision_id
        plan_id = issued.plan_id
        plan_fingerprint = issued.plan_fingerprint
        server_id = issued.server_id
        action_type = issued.action_type
        target = issued.target
        sandbox_validation_id = issued.sandbox_validation_id
        issued_at = issued.issued_at
        expires_at = issued.expires_at
        consumed_at = now

    repository.get_authorization = lambda authorization_id: Model()
    consumed = service.consume(issued.authorization_id)
    assert consumed.status is AutonomousAuthorizationStatus.CONSUMED
