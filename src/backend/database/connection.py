"""
Database Connection & Spatial Helper Setup
Supports SQLite with registered spatial functions, and PostgreSQL/PostGIS in production.
"""

import math
import os
import sqlite3
from typing import Generator, Any
from contextlib import contextmanager

try:
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import declarative_base, sessionmaker, Session
    SQLALCHEMY_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    SQLALCHEMY_AVAILABLE = False
    create_engine = None
    event = None
    declarative_base = None
    sessionmaker = None
    Session = Any

from src.backend.config import settings


def _haversine_sql(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance calculation in kilometers registered as a custom SQLite function."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999999.0
    r = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return r * c


if SQLALCHEMY_AVAILABLE:
    # Ensure data directory exists
    if settings.DATABASE_URL.startswith("sqlite:///"):
        db_file_path = settings.DATABASE_URL.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_file_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    # Connect args for SQLite to allow multi-threaded FastAPI workers and 5s busy timeout
    connect_args = {
        "check_same_thread": False,
        "timeout": 15
    } if settings.DATABASE_URL.startswith("sqlite") else {}

    # Engine configuration with connection pooling and health pre-ping
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_size=10 if not settings.DATABASE_URL.startswith("sqlite") else 5,
        max_overflow=20 if not settings.DATABASE_URL.startswith("sqlite") else 10,
        pool_timeout=15,
        pool_recycle=1800
    )

    @event.listens_for(engine, "connect")
    def configure_sqlite_pragmas(dbapi_connection, connection_record):
        """
        Configures SQLite high-concurrency pragmas:
        - WAL Mode: Non-blocking concurrent reads during writes.
        - Busy Timeout: Waits up to 5,000ms on locks rather than throwing immediate errors.
        - Synchronous Normal: High throughput with crash-resilient WAL.
        - Spatial Haversine: Registers fast in-database distance function.
        """
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA busy_timeout=5000;")
            cursor.execute("PRAGMA cache_size=-64000;")  # 64MB RAM page cache
            cursor.close()
            dbapi_connection.create_function("haversine_km", 4, _haversine_sql)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
else:
    engine = None
    class DummySession:
        def query(self, *args, **kwargs):
            return self
        def filter(self, *args, **kwargs):
            return self
        def all(self):
            return []
        def first(self):
            return None
        def add(self, *args, **kwargs):
            pass
        def commit(self):
            pass
        def rollback(self):
            pass
        def close(self):
            pass
    def SessionLocal():
        return DummySession()
    class Base:
        pass


def get_db():
    """FastAPI Dependency that yields an active database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """Context manager yielding a database session with guaranteed cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

