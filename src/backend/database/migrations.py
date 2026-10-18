"""
Database Migrations and Schema Manager
Initializes all database tables, verifies integrity, and provides schema management.
"""

import logging
from sqlalchemy import inspect
from src.backend.database.connection import engine, Base
import src.backend.database.models  # Ensure all models are registered with Base

logger = logging.getLogger("pathfinder.migrations")


def run_migrations():
    """
    Creates all defined tables and indexes if they do not exist.
    Safe to run repeatedly on startup or during test initialization.
    """
    logger.info("Running database migrations...")
    Base.metadata.create_all(bind=engine)
    
    # Verify tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Database tables verified ({len(tables)} tables): {', '.join(tables)}")
    return tables


def reset_database():
    """Drops all tables and recreates them. Used for test harnesses."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
