"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.infrastructure.database.models.report_analysis_source، app.infrastructure.database.session.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from sqlalchemy import delete, select
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.report_analysis_source import (
    ReportAnalysisSourceModel,
)
from app.infrastructure.database.session import SessionLocal


class AnalysisSourceRepository:
    """
    يمثل AnalysisSourceRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

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

    def replace_for_analysis(
        self,
        *,
        analysis_id: int,
        sources: list[dict],
    ) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى replace_for_analysis؛ المدخلات المهمة: analysis_id، sources.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            session.execute(
                delete(ReportAnalysisSourceModel).where(
                    ReportAnalysisSourceModel.analysis_id
                    == analysis_id
                )
            )
            for source in sources:
                session.add(
                    ReportAnalysisSourceModel(
                        analysis_id=analysis_id,
                        **source,
                    )
                )
            session.commit()

    def list_by_analysis_id(
        self,
        analysis_id: int,
    ) -> list[ReportAnalysisSourceModel]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_by_analysis_id؛ المدخلات المهمة: analysis_id.
        تعيد list[ReportAnalysisSourceModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            statement = (
                select(ReportAnalysisSourceModel)
                .where(
                    ReportAnalysisSourceModel.analysis_id
                    == analysis_id
                )
                .order_by(
                    ReportAnalysisSourceModel.rank.asc()
                    .nulls_first(),
                    ReportAnalysisSourceModel.id.asc(),
                )
            )
            return list(
                session.scalars(statement).all()
            )
