"""
بنية قاعدة البيانات من engine/session/base.

الموقع في المعمارية: Database infrastructure.
يُستدعى بواسطة: composition وrepositories.
يعتمد مباشرة على: app.infrastructure.database.engine.
الحد المعماري: لا يقرر domain behavior؛ يوفر الاتصال والجلسات.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.database.engine import engine


SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_database_session() -> Generator[
    Session,
    None,
    None,
]:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Database infrastructure.

    تُستدعى عندما يصل workflow إلى get_database_session؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد Generator[Session, None, None] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()