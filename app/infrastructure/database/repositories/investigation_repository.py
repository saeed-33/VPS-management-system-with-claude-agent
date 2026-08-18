"""
حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.investigation import (
    InvestigationModel,
    InvestigationSpecialistCandidateModel,
)
from app.infrastructure.database.models.server import ServerModel
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.investigation import InvestigationStatus
from app.core.contracts.investigations import PersistInvestigationDTO


class InvestigationRepository:
    """
    مسؤول عن حفظ حالة التحقيق ومنع تكرار تشغيل المتخصص وتثبيت نتائجه.
    """
    def __init__(self, session_factory: sessionmaker = SessionLocal) -> None:
        """
        يهيئ مستودع حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
        """
        self._session_factory = session_factory

    def create(self, data: PersistInvestigationDTO) -> InvestigationModel:
        """
        ينشئ أو يحدث سجلًا في حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = InvestigationModel(
            investigation_id=data.investigation_id,
            server_id=data.server_id,
            report_id=data.report_id,
            analysis_id=data.analysis_id,
            status=data.status,
            should_investigate=data.should_investigate,
            routing_reasons=list(data.routing_reasons),
            detected_domains=list(data.detected_domains),
            unmatched_issue_indexes=list(data.unmatched_issue_indexes),
            registry_size=data.registry_size,
            candidate_limit=data.candidate_limit,
            selection_limit=data.selection_limit,
            max_specialists=data.max_specialists,
            max_rounds=data.max_rounds,
            max_actions=data.max_actions,
            routing_version=data.routing_version,
            investigation_metadata=dict(data.metadata),
        )
        model.candidates = [
            InvestigationSpecialistCandidateModel(
                specialist_definition_id=item.specialist_definition_id,
                specialist_slug=item.specialist_slug,
                specialist_name=item.specialist_name,
                score=item.score,
                priority=item.priority,
                candidate_rank=item.candidate_rank,
                is_selected=item.is_selected,
                selected_rank=item.selected_rank,
                matched_domains=list(item.matched_domains),
                matched_trigger_hints=list(item.matched_trigger_hints),
                matched_issue_indexes=list(item.matched_issue_indexes),
            )
            for item in data.candidates
        ]

        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            _ = model.candidates
            return model

    def update_runtime_snapshot(
        self,
        *,
        investigation_id: str,
        status: str,
        metadata: dict,
    ) -> InvestigationModel:
        """
        يحدّث انتقالًا أو إعدادًا في حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.scalar(
                select(
                    InvestigationModel
                ).where(
                    InvestigationModel
                    .investigation_id
                    == investigation_id
                )
            )

            if model is None:
                raise ValueError(
                    "Investigation not found: "
                    f"{investigation_id}"
                )

            model.status = status

            model.investigation_metadata = (
                dict(metadata)
            )

            session.add(
                model
            )

            session.commit()

            session.refresh(
                model
            )

            _ = model.candidates

            return model

    def merge_runtime_snapshot(
        self,
        *,
        investigation_id: str,
        status: str,
        merge: Callable[[InvestigationModel, dict], dict],
    ) -> InvestigationModel:
        """
        يدمج تحديثًا جزئيًا في لقطة تشغيل التحقيق دون حذف الأدلة أو النتائج السابقة.

        يستخدم الدمج لاستقبال تقدم متزامن من المتخصصين مع إبقاء الحالة الكاملة
        قابلة للقراءة بعد كل تحديث.
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
                model.status = status
                model.investigation_metadata = merge(
                    model,
                    dict(model.investigation_metadata or {}),
                )
                session.add(model)
                session.flush()
                session.refresh(model)
                _ = model.candidates
                return model

    def reserve_specialist(
        self,
        *,
        investigation_id: str,
        specialist_slug: str,
        ownership_token: str,
        lease_seconds: int = 900,
    ) -> dict:
        """
        يحجز سجلًا في حالة التحقيق ولقطات تشغيله وحجوز مهام المتخصصين ونتائجهم لمنع تنفيذ متزامن أو تكرار الأثر نفسه.
        """
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=lease_seconds)

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
                runs = list(snapshot.get("specialist_runs") or [])
                existing = next(
                    (item for item in runs if item.get("specialist_slug") == specialist_slug),
                    None,
                )
                terminal_statuses = {"completed", "failed", "cancelled"}
                if existing is not None and existing.get("status") in terminal_statuses:
                    return {
                        "status": "completed",
                        "run": existing,
                        "actions_used": int(snapshot.get("actions_used") or 0),
                    }

                reservations = dict(metadata.get("specialist_reservations") or {})
                current = reservations.get(specialist_slug)
                if current is not None:
                    try:
                        current_expires = datetime.fromisoformat(str(current["expires_at"]))
                    except (KeyError, TypeError, ValueError):
                        current_expires = now
                    if current_expires > now:
                        return {
                            "status": "in_progress",
                            "run": existing,
                            "actions_used": int(snapshot.get("actions_used") or 0),
                            "owner": current,
                        }

                reservations[specialist_slug] = {
                    "token": ownership_token,
                    "claimed_at": now.isoformat(),
                    "expires_at": expires.isoformat(),
                }
                metadata["specialist_reservations"] = reservations
                model.status = "investigating"
                model.investigation_metadata = metadata
                session.add(model)

                return {
                    "status": "reserved",
                    "run": existing,
                    "actions_used": int(snapshot.get("actions_used") or 0),
                    "selected_specialists": [
                        candidate.specialist_slug
                        for candidate in model.candidates
                        if candidate.is_selected
                    ],
                }

    def promote_next_candidate(self, *, investigation_id: str) -> dict | None:
        """
        يضيف المرشح التالي إلى موجة التحقيق ضمن حد المتخصصين المسموح.

        يستخدم هذا المسار عندما تنتهي الموجة الحالية بلا أدلة؛ فلا يعيد حجز
        متخصص مكتمل، ولا يترك التحقيق عالقاً على المرشحين الأوائل فقط.
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

                candidates = list(model.candidates)
                selected = [item for item in candidates if item.is_selected]
                if len(selected) >= model.max_specialists:
                    return None

                next_candidate = next(
                    (item for item in candidates if not item.is_selected),
                    None,
                )
                if next_candidate is None:
                    return None

                next_candidate.is_selected = True
                next_candidate.selected_rank = len(selected) + 1
                model.status = InvestigationStatus.INVESTIGATING.value
                session.add(next_candidate)
                session.add(model)
                return {
                    "specialist_slug": next_candidate.specialist_slug,
                    "selected_rank": next_candidate.selected_rank,
                }

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
