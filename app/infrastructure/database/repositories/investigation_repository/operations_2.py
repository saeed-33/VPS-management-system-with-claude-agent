"""
حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.investigation.investigation import InvestigationModel
from app.infrastructure.database.models.investigation.candidate import InvestigationSpecialistCandidateModel
from app.infrastructure.database.models.server.server import ServerModel
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.investigation.investigation_status import InvestigationStatus
from app.core.contracts.investigations.persist_investigation_dto import PersistInvestigationDTO


class _InvestigationRepositoryMixin2:
    """ينظم مجموعة من عمليات المستودع."""

    def close_without_evidence(self, *, investigation_id: str) -> InvestigationModel:
        """
        ينهي تحقيقاً لا يملك أدلة بعد استنفاد المرشحين دون إعادة جدولة لا نهائية.
        """
        with self._session_factory() as session:
            with session.begin():
                model = session.scalar(
                    select(InvestigationModel)
                    .where(InvestigationModel.investigation_id == investigation_id)
                    .with_for_update()
                )
                if model is None:
                    raise ValueError(f"Investigation not found: {investigation_id}")

                metadata = dict(model.investigation_metadata or {})
                snapshot = dict(metadata.get("runtime_snapshot") or {})
                snapshot["status"] = InvestigationStatus.NO_EVIDENCE_FOUND.value
                snapshot["final_diagnosis_available"] = False
                runtime_metadata = dict(snapshot.get("metadata") or {})
                runtime_metadata["completion_reason"] = "no_evidence_found"
                runtime_metadata["remaining_specialists"] = []
                snapshot["metadata"] = runtime_metadata
                metadata["runtime_snapshot"] = snapshot
                metadata["no_evidence_found_reason"] = (
                    "All selected specialists completed without findings and "
                    "no unselected candidates remain within the investigation budget."
                )
                model.status = InvestigationStatus.NO_EVIDENCE_FOUND.value
                model.investigation_metadata = metadata
                session.add(model)
                session.flush()
                session.refresh(model)
                _ = model.candidates
                return model

    def finalize_specialist(
        self,
        *,
        investigation_id: str,
        specialist_slug: str,
        ownership_token: str,
        merge: Callable[[InvestigationModel, dict], tuple[str, dict]],
    ) -> InvestigationModel:
        """
        يثبت النتيجة النهائية في حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم قبل إعلان اكتمال المرحلة التالية.
        """
        with self._session_factory() as session:
            with session.begin():
                model = session.scalar(
                    select(InvestigationModel)
                    .where(InvestigationModel.investigation_id == investigation_id)
                    .with_for_update()
                )
                if model is None:
                    raise ValueError(f"Investigation not found: {investigation_id}")

                metadata = dict(model.investigation_metadata or {})
                reservations = dict(metadata.get("specialist_reservations") or {})
                claim = reservations.get(specialist_slug)
                if claim is None or claim.get("token") != ownership_token:
                    snapshot = dict(metadata.get("runtime_snapshot") or {})
                    existing = next(
                        (
                            item
                            for item in (snapshot.get("specialist_runs") or [])
                            if item.get("specialist_slug") == specialist_slug
                        ),
                        None,
                    )
                    if existing is not None and existing.get("status") in {"completed", "failed", "cancelled"}:
                        return model
                    raise ValueError("Specialist reservation ownership was lost.")

                status, merged = merge(model, metadata)
                reservations.pop(specialist_slug, None)
                merged["specialist_reservations"] = reservations
                model.status = status
                model.investigation_metadata = merged
                session.add(model)
                session.flush()
                session.refresh(model)
                _ = model.candidates
                return model

    def persist_finalization(
        self,
        *,
        investigation_id: str,
        merge: Callable[[InvestigationModel, dict], tuple[str, dict]],
    ) -> InvestigationModel:
        """
        يثبت النتيجة النهائية في حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم قبل إعلان اكتمال المرحلة التالية.
        """
        with self._session_factory() as session:
            with session.begin():
                model = session.scalar(
                    select(InvestigationModel)
                    .where(InvestigationModel.investigation_id == investigation_id)
                    .with_for_update()
                )
                if model is None:
                    raise ValueError(f"Investigation not found: {investigation_id}")
                status, metadata = merge(model, dict(model.investigation_metadata or {}))
                model.status = status
                model.investigation_metadata = metadata
                session.add(model)
                session.flush()
                session.refresh(model)
                _ = model.candidates
                return model

    def get_by_investigation_id(
        self,
        investigation_id: str,
    ) -> InvestigationModel | None:
        """
        يسترجع سجلًا من حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            model = session.scalar(
                select(InvestigationModel).where(
                    InvestigationModel.investigation_id == investigation_id
                )
            )
            if model is not None:
                _ = model.candidates
            return model

    def list_recent(
        self,
        *,
        limit: int = 100,
        server_id: int | None = None,
    ) -> list[InvestigationModel]:
        """
        يعرض قائمة مرتبة من حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        if limit < 1:
            raise ValueError("limit must be >= 1.")

        statement = (
            select(InvestigationModel)
            .order_by(
                InvestigationModel.created_at.desc(),
                InvestigationModel.id.desc(),
            )
            .limit(limit)
        )

        if server_id is not None:
            statement = statement.where(
                InvestigationModel.server_id == server_id
            )

        with self._session_factory() as session:
            models = list(
                session.scalars(statement).all()
            )
            for model in models:
                _ = model.candidates
            return models

    def list_recoverable(
        self,
        *,
        limit: int = 1,
    ) -> list[InvestigationModel]:
        """
        يعرض أقدم التحقيقات التي انقطع تشغيلها بعد التوجيه.

        يمرر فقط التحقيقات التي تحتاج تحقيقًا وسيرفرها مفعل وغير متوقف، حتى
        لا يعيد العامل تشغيل سجلات تخص سيرفرًا أوقفه المشغل عمدًا.
        """
        if limit < 1:
            raise ValueError("limit must be >= 1.")

        statement = (
            select(InvestigationModel)
            .join(
                ServerModel,
                ServerModel.id == InvestigationModel.server_id,
            )
            .where(
                InvestigationModel.status.in_(
                    {"created", "investigating", "waiting_for_evidence"}
                ),
                InvestigationModel.should_investigate.is_(True),
                ServerModel.monitor_enabled.is_(True),
                ServerModel.status != "offline",
            )
            .order_by(
                InvestigationModel.created_at.asc(),
                InvestigationModel.id.asc(),
            )
            .limit(limit)
        )

        with self._session_factory() as session:
            models = list(session.scalars(statement).all())
            for model in models:
                _ = model.candidates
            return models

    def list_by_report_id(self, report_id: int) -> list[InvestigationModel]:
        """
        يعرض قائمة مرتبة من حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            models = list(
                session.scalars(
                    select(InvestigationModel)
                    .where(InvestigationModel.report_id == report_id)
                    .order_by(
                        InvestigationModel.created_at.desc(),
                        InvestigationModel.id.desc(),
                    )
                ).all()
            )
            for model in models:
                _ = model.candidates
            return models
