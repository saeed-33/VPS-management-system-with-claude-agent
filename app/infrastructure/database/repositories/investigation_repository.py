"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.infrastructure.database.models.investigation، app.infrastructure.database.session، app.core.contracts.investigations.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.investigations import PersistInvestigationDTO


class InvestigationRepository:
    """
    يمثل InvestigationRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه application capabilities
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, session_factory: sessionmaker = SessionLocal) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: session_factory.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._session_factory = session_factory

    def create(self, data: PersistInvestigationDTO) -> InvestigationModel:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى create؛ المدخلات المهمة: data.
        تعيد InvestigationModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update_runtime_snapshot؛ المدخلات المهمة: investigation_id، status، metadata.
        تعيد InvestigationModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        """Lock, merge, and commit the current metadata in one short transaction."""
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
        """Short transaction that claims one Specialist execution.

        The lease is stored beside the runtime projection so a crashed worker
        cannot permanently strand a selected Specialist. The expensive loop
        is intentionally never run while this row lock is held.
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

    def finalize_specialist(
        self,
        *,
        investigation_id: str,
        specialist_slug: str,
        ownership_token: str,
        merge: Callable[[InvestigationModel, dict], tuple[str, dict]],
    ) -> InvestigationModel:
        """Atomically merge one accepted result and release its lease."""
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
        """Atomically attach deterministic diagnosis/narrative to latest state."""
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_investigation_id؛ المدخلات المهمة: investigation_id.
        تعيد InvestigationModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_recent؛ المدخلات المهمة: limit، server_id.
        تعيد list[InvestigationModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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

    def list_by_report_id(self, report_id: int) -> list[InvestigationModel]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_by_report_id؛ المدخلات المهمة: report_id.
        تعيد list[InvestigationModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
