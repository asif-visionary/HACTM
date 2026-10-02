"""
Database connection and session factory for HACTM.
Uses SQLAlchemy 2.0 with support for SQLite and PostgreSQL.
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from hactm.core.config import settings

# Engine configuration
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
    future=True,
)

# Enable SQLite WAL and foreign keys for high throughput and consistency
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initializes all database tables and ensures schema evolution."""
    import hactm.storage.models  # Ensure models are imported before creating tables
    Base.metadata.create_all(bind=engine)

    # SQLite lightweight column migration for newly added fields
    if settings.DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            # Check network_models columns
            result = conn.exec_driver_sql("PRAGMA table_info(network_models)")
            existing_cols = {row[1] for row in result}
            if "training_samples" not in existing_cols and "model_id" in existing_cols:
                conn.exec_driver_sql("ALTER TABLE network_models ADD COLUMN training_samples INTEGER DEFAULT 0")
            if "artifact_path" not in existing_cols and "model_id" in existing_cols:
                conn.exec_driver_sql("ALTER TABLE network_models ADD COLUMN artifact_path VARCHAR(512)")

            # Check hypothesis_results columns
            res_hypo = conn.exec_driver_sql("PRAGMA table_info(hypothesis_results)")
            hypo_cols = {row[1] for row in res_hypo}
            if "effect_size" not in hypo_cols and "hypothesis_id" in hypo_cols:
                conn.exec_driver_sql("ALTER TABLE hypothesis_results ADD COLUMN effect_size FLOAT")

            conn.commit()

