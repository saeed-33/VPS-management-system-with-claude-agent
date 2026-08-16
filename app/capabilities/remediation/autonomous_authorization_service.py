"""
إدارة تفويضات التنفيذ الآلي قصيرة العمر.

تنشئ الخدمة تفويضًا مرتبطًا بالخطة والسيرفر، وتستهلكه مرة واحدة أو تسترجعه
للتحقق من حالته قبل السماح بأي أثر تنفيذي.
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
    يدير إنشاء التفويضات الآلية والتحقق من صلاحيتها واستهلاكها لمرة واحدة.
    """
    def __init__(self, *, repository) -> None:
        """
        يربط مستودع التفويضات والساعة الافتراضية ومدة التفويض.
        """
        self._repository = repository

    def issue(self, *, decision, sandbox_validation_id: str, ttl_seconds: int = 300) -> AutonomousAuthorization:
        """
        ينشئ تفويضًا جديدًا مرتبطًا بالخطة والسيرفر والأفعال المسموحة ووقت الانتهاء.
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
        يتحقق من التفويض ثم يعلّمه مستخدمًا مرة واحدة ويربطه بقرار التنفيذ.
        """
        consumed = self._repository.consume_authorization(authorization_id, now=utc_now())
        return replace(
            self._authorization_by_id(authorization_id),
            status=AutonomousAuthorizationStatus.CONSUMED,
            consumed_at=getattr(consumed, "consumed_at", utc_now()),
        )

    def get(self, authorization_id: str) -> AutonomousAuthorization:
        """
        يجلب تفويضًا صالحًا للعرض أو التحقق ويرفع خطأ عند غيابه.
        """
        return self._authorization_by_id(authorization_id)

    def _authorization_by_id(self, authorization_id: str) -> AutonomousAuthorization:
        """
        يسترجع التفويض من المستودع ويحوّل غيابه إلى خطأ صريح.
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
