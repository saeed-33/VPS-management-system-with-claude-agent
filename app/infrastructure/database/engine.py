from sqlalchemy import create_engine

from app.shared.config import settings
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
    # مهم: يجب استيراد جميع Models قبل create_all
    import app.shared.database.models  # noqa: F401

    Base.metadata.create_all(engine)