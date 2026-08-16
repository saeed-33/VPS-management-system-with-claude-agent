"""توفير جلسات قاعدة البيانات لخدمات ومستودعات التطبيق."""
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
    يفتح جلسة قاعدة بيانات للطلب ثم يغلقها مهما كانت نتيجة العملية.

    تستخدم المستودعات الجلسة لقراءة وحفظ التقارير والحالات، بينما يضمن الإغلاق
    النهائي عدم بقاء اتصال أو موارد مرتبطة بطلب انتهى.
    """
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
