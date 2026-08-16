"""
جزء من Remediation من التشخيص والاقتراح حتى sandbox/authorization والتنفيذ.

الموقع في المعمارية: Application capability / remediation.
يُستدعى بواسطة: Admin API أو MCP.
يعتمد مباشرة على: app.core.contracts.autonomous_remediation، app.core.utils.datetime.
الحد المعماري: لا يسمح write operation بمجرد اقتراح LLM.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from datetime import timedelta
from dataclasses import replace
from uuid import uuid4

from app.core.contracts.autonomous_remediation import (
    AutonomousAuthorization,
    AutonomousAuthorizationStatus,
)
from app.core.utils.datetime import utc_now


class AutonomousAuthorizationService:
    """
    يمثل AutonomousAuthorizationService مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, *, repository) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: repository.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._repository = repository

    def issue(self, *, decision, sandbox_validation_id: str, ttl_seconds: int = 300) -> AutonomousAuthorization:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى issue؛ المدخلات المهمة: decision، sandbox_validation_id، ttl_seconds.
        تعيد AutonomousAuthorization أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        now = utc_now()
        authorization = AutonomousAuthorization(
            authorization_id=str(uuid4()), token=str(uuid4()), status=AutonomousAuthorizationStatus.VALID,
            policy_id=str(decision.policy_id), policy_version=int(decision.policy_version or 0),
            decision_id=decision.decision_id, plan_id=str(decision.plan_id), plan_fingerprint=str(decision.plan_fingerprint),
            server_id=int(decision.server_id or 0), action_type=str(decision.action_type), target=str(decision.target),
            sandbox_validation_id=sandbox_validation_id, issued_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )
        self._repository.create_authorization(authorization)
        return authorization

    def consume(self, authorization_id: str):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى consume؛ المدخلات المهمة: authorization_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        consumed = self._repository.consume_authorization(authorization_id, now=utc_now())
        return replace(
            self._authorization_by_id(authorization_id),
            status=AutonomousAuthorizationStatus.CONSUMED,
            consumed_at=getattr(consumed, "consumed_at", utc_now()),
        )

    def get(self, authorization_id: str) -> AutonomousAuthorization:
        """Load an existing authorization for crash recovery without issuing another one."""
        return self._authorization_by_id(authorization_id)

    def _authorization_by_id(self, authorization_id: str) -> AutonomousAuthorization:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى _authorization_by_id؛ المدخلات المهمة: authorization_id.
        تعيد AutonomousAuthorization أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        model = self._repository.get_authorization(authorization_id)
        if model is None:
            raise ValueError("Autonomous authorization not found.")
        return AutonomousAuthorization(
            authorization_id=model.authorization_id, token=model.token,
            status=AutonomousAuthorizationStatus(model.status), policy_id=model.policy_id,
            policy_version=model.policy_version, decision_id=model.decision_id,
            plan_id=model.plan_id, plan_fingerprint=model.plan_fingerprint,
            server_id=model.server_id, action_type=model.action_type, target=model.target,
            sandbox_validation_id=model.sandbox_validation_id, issued_at=model.issued_at,
            expires_at=model.expires_at, consumed_at=model.consumed_at,
        )
