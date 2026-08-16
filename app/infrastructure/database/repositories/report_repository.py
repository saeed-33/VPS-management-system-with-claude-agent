"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.core.contracts.reports، app.infrastructure.database.models.command_execution، app.infrastructure.database.models.monitoring_report، app.infrastructure.database.models.server، app.infrastructure.database.session.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import (
    selectinload,
    sessionmaker,
)

from app.core.contracts.reports import MonitoringReportData
from app.infrastructure.database.models.command_execution import (
    CommandExecutionModel,
)
from app.infrastructure.database.models.monitoring_report import (
    MonitoringReportModel,
)
from app.infrastructure.database.models.server import (
    ServerModel,
)
from app.infrastructure.database.session import SessionLocal


class ReportRepository:
    """
    يمثل ReportRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

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
        report: MonitoringReportData,
    ) -> int:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى create؛ المدخلات المهمة: report.
        تعيد int أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        report_model = MonitoringReportModel(
            server_id=report.server_id,
            status=report.status.value,
            started_at=report.started_at,
            finished_at=report.finished_at,
            duration_ms=report.duration_ms,
            connection_successful=(
                report.connection_successful
            ),
            commands_total=report.commands_total,
            commands_succeeded=(
                report.commands_succeeded
            ),
            commands_failed=(
                report.commands_failed
            ),
            error_message=report.error_message,
        )

        for execution in report.executions:
            execution_model = CommandExecutionModel(
                command_id=execution.command_id,
                command_name=execution.command_name,
                command_text=execution.command_text,
                execution_order=(
                    execution.execution_order
                ),
                success=execution.success,
                exit_status=execution.exit_status,
                stdout=execution.stdout,
                stderr=execution.stderr,
                error_message=(
                    execution.error_message
                ),
                fingerprint_strategy=(
                    execution.fingerprint_strategy
                ),
                fingerprint_config=(
                    execution.fingerprint_config
                ),
                started_at=execution.started_at,
                finished_at=execution.finished_at,
                duration_ms=execution.duration_ms,
            )

            report_model.executions.append(
                execution_model
            )

        with self._session_factory() as session:
            session.add(report_model)
            session.commit()
            session.refresh(report_model)

            return report_model.id

    def get_by_id(
        self,
        report_id: int,
    ) -> MonitoringReportModel | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_id؛ المدخلات المهمة: report_id.
        تعيد MonitoringReportModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            statement = (
                select(MonitoringReportModel)
                .options(
                    selectinload(
                        MonitoringReportModel.executions
                    )
                )
                .where(
                    MonitoringReportModel.id
                    == report_id
                )
            )

            return session.scalar(statement)

    def list_reports(
        self,
        *,
        server_id: int | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[
        tuple[MonitoringReportModel, ServerModel]
    ]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_reports؛ المدخلات المهمة: server_id، status، offset، limit.
        تعيد list[tuple[MonitoringReportModel, ServerModel]] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            statement = (
                select(
                    MonitoringReportModel,
                    ServerModel,
                )
                .join(
                    ServerModel,
                    ServerModel.id
                    == MonitoringReportModel.server_id,
                )
                .order_by(
                    MonitoringReportModel.id.desc()
                )
                .offset(offset)
                .limit(limit)
            )

            if server_id is not None:
                statement = statement.where(
                    MonitoringReportModel.server_id
                    == server_id
                )

            if status is not None:
                statement = statement.where(
                    MonitoringReportModel.status
                    == status
                )

            return list(
                session.execute(statement).all()
            )

    def count_reports(
        self,
        *,
        server_id: int | None = None,
        status: str | None = None,
    ) -> int:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى count_reports؛ المدخلات المهمة: server_id، status.
        تعيد int أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            statement = select(
                func.count(
                    MonitoringReportModel.id
                )
            )

            if server_id is not None:
                statement = statement.where(
                    MonitoringReportModel.server_id
                    == server_id
                )

            if status is not None:
                statement = statement.where(
                    MonitoringReportModel.status
                    == status
                )

            return int(
                session.scalar(statement) or 0
            )

    def get_with_server(
        self,
        report_id: int,
    ) -> tuple[
        MonitoringReportModel,
        ServerModel,
    ] | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_with_server؛ المدخلات المهمة: report_id.
        تعيد tuple[MonitoringReportModel, ServerModel] | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            statement = (
                select(
                    MonitoringReportModel,
                    ServerModel,
                )
                .join(
                    ServerModel,
                    ServerModel.id
                    == MonitoringReportModel.server_id,
                )
                .options(
                    selectinload(
                        MonitoringReportModel.executions
                    )
                )
                .where(
                    MonitoringReportModel.id
                    == report_id
                )
            )

            return session.execute(
                statement
            ).first()