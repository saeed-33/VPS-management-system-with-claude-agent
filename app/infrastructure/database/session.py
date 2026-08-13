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
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()