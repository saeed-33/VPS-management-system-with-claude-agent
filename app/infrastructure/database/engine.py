"""
بنية قاعدة البيانات من engine/session/base.

الموقع في المعمارية: Database infrastructure.
يُستدعى بواسطة: composition وrepositories.
يعتمد مباشرة على: app.core.config، app.infrastructure.database.base.
الحد المعماري: لا يقرر domain behavior؛ يوفر الاتصال والجلسات.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from sqlalchemy import create_engine

from app.core.config import settings
from app.infrastructure.database.base import Base


engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
)


def create_database_tables() -> None:
    """
    ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Database infrastructure.

    تُستدعى عندما يصل workflow إلى create_database_tables؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    # مهم: يجب استيراد جميع Models قبل create_all
    import app.infrastructure.database.models  # noqa: F401

    Base.metadata.create_all(engine)