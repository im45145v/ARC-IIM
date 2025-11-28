"""
Pytest configuration and fixtures for testing.
"""

import os
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from alumni_system.database.models import Base


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create a test database engine.
    
    Uses an in-memory SQLite database for fast, isolated testing.
    """
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """
    Create a new database session for a test.
    
    Each test gets a fresh session that is rolled back after the test completes.
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def clean_db_session(test_db_engine) -> Generator[Session, None, None]:
    """
    Create a clean database session that commits changes.
    
    Used for testing database initialization and migration logic.
    This fixture cleans up all data after the test to maintain isolation.
    """
    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()
    
    yield session
    
    # Clean up all data after test to maintain isolation
    try:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()
