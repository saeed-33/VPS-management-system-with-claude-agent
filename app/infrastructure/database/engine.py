"""إنشاء محرك الاتصال بقاعدة البيانات وتهيئة جداول الحالة التشغيلية."""
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
    ينشئ جداول نماذج التطبيق عند بدء الخدمة إذا لم تكن موجودة.

    يحمّل جميع نماذج قاعدة البيانات قبل إنشاء الجداول حتى تعرف metadata علاقات
    السيرفر والتقرير والتحليل والتحقيق والمعالجة كاملة.
    """
    # يجب تسجيل جميع النماذج قبل الإنشاء حتى لا يبدأ التخزين بجداول ناقصة.
    import app.infrastructure.database.models  # noqa: F401

    Base.metadata.create_all(engine)
