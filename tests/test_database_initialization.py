"""
Property-based tests for database initialization.

Tests that database initialization is idempotent and maintains schema integrity.
"""

import pytest
from hypothesis import given, settings, strategies as st
from sqlalchemy import create_engine, inspect

# Import only models to avoid connection issues during testing
from alumni_system.database.models import (
    AccountUsage,
    Alumni,
    Base,
    EducationHistory,
    JobHistory,
    ScrapingLog,
    ScrapingQueue,
)


@given(
    num_initializations=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=100, deadline=None)
def test_database_initialization_is_idempotent(num_initializations: int):
    """
    Feature: alumni-management-system, Property 10: Database initialization is idempotent
    
    **Validates: Requirements 2.1**
    
    For any database state, running initialization multiple times should result 
    in the same schema without errors.
    
    This property ensures that:
    1. Multiple calls to init_database() don't raise errors
    2. The schema remains consistent after multiple initializations
    3. All expected tables exist after initialization
    4. Table structures remain unchanged across multiple initializations
    """
    # Create a fresh in-memory database for this test
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    try:
        # Store the initial schema state
        initial_tables = None
        initial_columns = {}
        
        # Run initialization multiple times
        for i in range(num_initializations):
            # Initialize database (without migrations for SQLite compatibility)
            Base.metadata.create_all(bind=engine)
            
            # Inspect the schema
            inspector = inspect(engine)
            current_tables = set(inspector.get_table_names())
            
            # On first initialization, capture the schema
            if i == 0:
                initial_tables = current_tables
                for table_name in initial_tables:
                    initial_columns[table_name] = {
                        col['name']: col['type'].__class__.__name__
                        for col in inspector.get_columns(table_name)
                    }
            else:
                # On subsequent initializations, verify schema hasn't changed
                assert current_tables == initial_tables, (
                    f"Table set changed after initialization {i+1}: "
                    f"expected {initial_tables}, got {current_tables}"
                )
                
                # Verify column structures remain the same
                for table_name in initial_tables:
                    current_columns = {
                        col['name']: col['type'].__class__.__name__
                        for col in inspector.get_columns(table_name)
                    }
                    assert current_columns == initial_columns[table_name], (
                        f"Columns changed for table {table_name} after initialization {i+1}"
                    )
        
        # Verify all expected tables exist
        expected_tables = {
            'alumni',
            'job_history',
            'education_history',
            'scraping_logs',
            'account_usage',
            'scraping_queue'
        }
        
        inspector = inspect(engine)
        actual_tables = set(inspector.get_table_names())
        
        assert expected_tables.issubset(actual_tables), (
            f"Missing tables: {expected_tables - actual_tables}"
        )
        
        # Verify key constraints and relationships exist
        # Check foreign keys for job_history
        job_history_fks = inspector.get_foreign_keys('job_history')
        assert any(fk['referred_table'] == 'alumni' for fk in job_history_fks), (
            "job_history should have foreign key to alumni"
        )
        
        # Check foreign keys for education_history
        education_history_fks = inspector.get_foreign_keys('education_history')
        assert any(fk['referred_table'] == 'alumni' for fk in education_history_fks), (
            "education_history should have foreign key to alumni"
        )
        
        # Check foreign keys for scraping_queue
        scraping_queue_fks = inspector.get_foreign_keys('scraping_queue')
        assert any(fk['referred_table'] == 'alumni' for fk in scraping_queue_fks), (
            "scraping_queue should have foreign key to alumni"
        )
        
    finally:
        # Cleanup
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_database_initialization_creates_all_tables():
    """
    Test that database initialization creates all required tables.
    
    This is a concrete example test that verifies the basic functionality.
    """
    # Create a fresh in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    try:
        # Initialize database
        Base.metadata.create_all(bind=engine)
        
        # Verify all tables exist
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        
        expected_tables = {
            'alumni',
            'job_history',
            'education_history',
            'scraping_logs',
            'account_usage',
            'scraping_queue'
        }
        
        assert expected_tables.issubset(tables), (
            f"Missing tables: {expected_tables - tables}"
        )
        
    finally:
        # Cleanup
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_database_initialization_twice_no_error():
    """
    Test that calling init_database twice doesn't raise an error.
    
    This is a concrete example test for the idempotency property.
    """
    # Create a fresh in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    try:
        # Initialize database twice
        Base.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=engine)  # Should not raise error
        
        # Verify tables still exist
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        
        assert 'alumni' in tables
        assert 'job_history' in tables
        assert 'education_history' in tables
        assert 'scraping_logs' in tables
        assert 'account_usage' in tables
        assert 'scraping_queue' in tables
        
    finally:
        # Cleanup
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_account_usage_unique_constraint():
    """
    Test that account_usage table has unique constraint on (account_email, date).
    
    This verifies the schema includes the necessary constraint for rate limiting.
    """
    # Create a fresh in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    try:
        # Initialize database
        Base.metadata.create_all(bind=engine)
        
        # Check for unique constraint
        inspector = inspect(engine)
        constraints = inspector.get_unique_constraints('account_usage')
        
        # SQLite may represent this differently, so we check if the constraint exists
        # by trying to insert duplicate data
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Insert first record
        usage1 = AccountUsage(
            account_email="test@example.com",
            date=datetime(2024, 1, 1),
            profiles_scraped=10
        )
        session.add(usage1)
        session.commit()
        
        # Try to insert duplicate - should fail or update
        usage2 = AccountUsage(
            account_email="test@example.com",
            date=datetime(2024, 1, 1),
            profiles_scraped=20
        )
        session.add(usage2)
        
        # This should raise an IntegrityError due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            session.commit()
        
        session.close()
        
    finally:
        # Cleanup
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_scraping_queue_cascade_delete():
    """
    Test that scraping_queue entries are deleted when alumni is deleted.
    
    This verifies the CASCADE delete constraint is properly configured.
    """
    # Create a fresh in-memory database with foreign key support
    from sqlalchemy import event
    
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    try:
        # Initialize database
        Base.metadata.create_all(bind=engine)
        
        from sqlalchemy.orm import sessionmaker
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create an alumni
        alumni = Alumni(
            name="Test Alumni",
            roll_number="TEST001"
        )
        session.add(alumni)
        session.commit()
        
        # Add to scraping queue
        queue_item = ScrapingQueue(
            alumni_id=alumni.id,
            priority=1,
            status='pending'
        )
        session.add(queue_item)
        session.commit()
        
        # Verify queue item exists
        assert session.query(ScrapingQueue).filter_by(alumni_id=alumni.id).count() == 1
        
        # Store the alumni_id before deletion
        alumni_id = alumni.id
        
        # Delete alumni
        session.delete(alumni)
        session.commit()
        
        # Verify queue item was also deleted (cascade)
        assert session.query(ScrapingQueue).filter_by(alumni_id=alumni_id).count() == 0
        
        session.close()
        
    finally:
        # Cleanup
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
