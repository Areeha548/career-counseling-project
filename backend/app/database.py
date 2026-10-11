from pathlib import Path

from sqlalchemy import create_engine, event, inspect
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


def ensure_career_skill_metadata() -> None:
    """Add career-specific priority columns to existing SQLite catalogs once."""
    columns = {column["name"] for column in inspect(engine).get_columns("career_skills")}
    with engine.begin() as connection:
        if "priority" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE career_skills ADD COLUMN priority VARCHAR(12) NOT NULL DEFAULT 'medium'"
            )
        if "target_level" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE career_skills ADD COLUMN target_level INTEGER NOT NULL DEFAULT 2"
            )


def ensure_roadmap_step_metadata() -> None:
    """Add optional roadmap guidance columns without rebuilding existing tables."""
    inspector = inspect(engine)
    template_columns = {column["name"] for column in inspector.get_columns("roadmap_step_templates")}
    progress_columns = {column["name"] for column in inspector.get_columns("user_roadmap_step_progress")}
    with engine.begin() as connection:
        additions = {
            "resource_search": "VARCHAR(300)",
            "prerequisites": "TEXT",
            "estimated_minutes": "INTEGER NOT NULL DEFAULT 60",
        }
        for name, column_type in additions.items():
            if name not in template_columns:
                connection.exec_driver_sql(
                    f"ALTER TABLE roadmap_step_templates ADD COLUMN {name} {column_type}"
                )
        if "estimated_minutes_at_creation" not in progress_columns:
            connection.exec_driver_sql(
                "ALTER TABLE user_roadmap_step_progress "
                "ADD COLUMN estimated_minutes_at_creation INTEGER NOT NULL DEFAULT 60"
            )


def get_db():
    """Provide a database session and close it after the request."""
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
