from __future__ import annotations
"""SQLAlchemy engine and session management for SQLite."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase

from app.config import DATABASE_PATH, ensure_dirs

# ---------------------------------------------------------------------------
# Declarative Base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


# ---------------------------------------------------------------------------
# Engine singleton
# ---------------------------------------------------------------------------

_engine = None
_SessionFactory = None


def get_engine():
    """Get or create the SQLAlchemy engine (singleton)."""
    global _engine
    if _engine is None:
        ensure_dirs()
        url = f"sqlite:///{DATABASE_PATH}"
        _engine = create_engine(
            url,
            echo=False,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )
        # Enable WAL mode and foreign keys for SQLite
        @event.listens_for(_engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return _engine


def get_session_factory():
    """Get or create the scoped session factory."""
    global _SessionFactory
    if _SessionFactory is None:
        engine = get_engine()
        session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        _SessionFactory = scoped_session(session_factory)
    return _SessionFactory


def get_session():
    """Get a new session from the scoped factory."""
    factory = get_session_factory()
    return factory()


def init_db():
    """Create all tables in the database."""
    # Import all models so they register with Base.metadata
    import app.models.customer      # noqa: F401
    import app.models.measurement   # noqa: F401
    import app.models.order         # noqa: F401
    import app.models.payment       # noqa: F401
    import app.models.expense       # noqa: F401
    import app.models.settings      # noqa: F401
    import app.models.worker        # noqa: F401

    engine = get_engine()
    Base.metadata.create_all(engine)


def close_db():
    """Close engine connections gracefully."""
    global _engine, _SessionFactory
    if _SessionFactory is not None:
        _SessionFactory.remove()
        _SessionFactory = None
    if _engine is not None:
        _engine.dispose()
        _engine = None
