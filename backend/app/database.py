from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_FILE = Path(__file__).resolve().parent.parent / "career_mentor.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(connection, _connection_record) -> None:
    """Enable SQLite foreign-key checks for each pooled connection."""
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class used by the project's SQLAlchemy models."""


def get_db():
    """Provide a database session and close it after the request."""
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
