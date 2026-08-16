"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.infrastructure.database.models.agent_job، app.infrastructure.database.session، app.core.contracts.agent_jobs.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.agent_job import (
    AgentJobModel,
)
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.agent_jobs import (
    CreateAgentJobDTO,
    UpdateAgentJobDTO,
)


_MAX_ERROR_MESSAGE_LENGTH = 2000


def _bounded_error_message(value: str | None) -> str | None:
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

    تُستدعى عندما يصل workflow إلى _bounded_error_message؛ المدخلات المهمة: value.
    تعيد str | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    if value is None:
        return None
    return value[:_MAX_ERROR_MESSAGE_LENGTH]


class AgentJobRepository:
    """
    يمثل AgentJobRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه application capabilities
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: session_factory.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._session_factory = session_factory

    def create(
        self,
        data: CreateAgentJobDTO,
    ) -> AgentJobModel:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى create؛ المدخلات المهمة: data.
        تعيد AgentJobModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        model = AgentJobModel(
            job_id=data.job_id,
            job_type=data.job_type,
            server_id=data.server_id,
            status=data.status,
            claude_session_id=(
                data.claude_session_id
            ),
            job_metadata=dict(
                data.metadata
            ),
        )

        with self._session_factory() as session:
            session.add(
                model
            )
            session.commit()
            session.refresh(
                model
            )
            return model

    def update(
        self,
        job_id: str,
        data: UpdateAgentJobDTO,
    ) -> AgentJobModel:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update؛ المدخلات المهمة: job_id، data.
        تعيد AgentJobModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            model = session.scalar(
                select(AgentJobModel).where(
                    AgentJobModel.job_id == job_id
                )
            )

            if model is None:
                raise ValueError(
                    "Agent job not found: "
                    f"{job_id}"
                )

            model.status = data.status
            model.claude_session_id = (
                data.claude_session_id
                if data.claude_session_id is not None
                else model.claude_session_id
            )
            model.completed_at = data.completed_at
            model.error_code = data.error_code
            model.error_message = _bounded_error_message(
                data.error_message
            )
            model.turn_count = data.turn_count
            model.tool_call_count = (
                data.tool_call_count
            )
            model.usage_metadata = dict(
                data.usage_metadata
            )

            if data.metadata is not None:
                model.job_metadata = dict(
                    data.metadata
                )

            session.add(
                model
            )
            session.commit()
            session.refresh(
                model
            )
            return model

    def get_by_job_id(
        self,
        job_id: str,
    ) -> AgentJobModel | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_job_id؛ المدخلات المهمة: job_id.
        تعيد AgentJobModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            return session.scalar(
                select(AgentJobModel).where(
                    AgentJobModel.job_id == job_id
                )
            )

    def list_recent(
        self,
        *,
        limit: int = 100,
        server_id: int | None = None,
        status: str | None = None,
    ) -> list[AgentJobModel]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_recent؛ المدخلات المهمة: limit، server_id، status.
        تعيد list[AgentJobModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if limit < 1:
            raise ValueError(
                "limit must be >= 1."
            )

        statement = (
            select(AgentJobModel)
            .order_by(
                AgentJobModel.created_at.desc(),
                AgentJobModel.id.desc(),
            )
            .limit(limit)
        )

        if server_id is not None:
            statement = statement.where(
                AgentJobModel.server_id
                == server_id
            )

        if status is not None:
            statement = statement.where(
                AgentJobModel.status == status
            )

        with self._session_factory() as session:
            return list(
                session.scalars(
                    statement
                ).all()
            )

    def mark_unfinished_after_restart(
        self,
        *,
        statuses: tuple[str, ...],
        failed_status: str,
        error_code: str,
        error_message: str,
    ) -> int:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى mark_unfinished_after_restart؛ المدخلات المهمة: statuses، failed_status، error_code، error_message.
        تعيد int أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        updated = 0

        with self._session_factory() as session:
            models = list(
                session.scalars(
                    select(AgentJobModel).where(
                        AgentJobModel.status.in_(
                            statuses
                        )
                    )
                ).all()
            )

            for model in models:
                model.status = failed_status
                model.completed_at = datetime.now(
                    timezone.utc
                )
                model.error_code = error_code
                model.error_message = _bounded_error_message(
                    error_message
                )
                session.add(
                    model
                )
                updated += 1

            session.commit()

        return updated
