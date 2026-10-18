"""
Database Connection & Spatial Helper Setup
Supports SQLite with registered spatial functions, and PostgreSQL/PostGIS in production.
"""

import math
import os
import sqlite3
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from src.backend.config import settings

# Ensure data directory exists
if settings.DATABASE_URL.startswith("sqlite:///"):
    db_file_path = settings.DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_file_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

# Connect args for SQLite to allow multi-threaded FastAPI workers
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)


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


@event.listens_for(engine, "connect")
def register_sqlite_functions(dbapi_connection, connection_record):
    """Registers spatial distance math directly into SQLite connection."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        dbapi_connection.create_function("haversine_km", 4, _haversine_sql)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency that yields an active database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
