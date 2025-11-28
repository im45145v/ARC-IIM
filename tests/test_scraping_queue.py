"""
Tests for scraping queue CRUD operations.

Tests the functionality of adding, retrieving, and managing items in the scraping queue.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alumni_system.database.models import Alumni, Base, ScrapingQueue
from alumni_system.database.crud import (
    add_to_scraping_queue,
    get_next_from_queue,
    mark_queue_item_complete,
    mark_queue_item_failed,
    mark_queue_item_in_progress,
    get_queue_statistics,
    create_alumni,
)


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_add_to_scraping_queue(db_session):
    """Test adding an alumni to the scraping queue."""
    # Create an alumni
    alumni = create_alumni(
        db_session,
        name="Test Alumni",
        roll_number="TEST001"
    )
    
    # Add to queue
    queue_item = add_to_scraping_queue(db_session, alumni.id, priority=5)
    
    # Verify
    assert queue_item.alumni_id == alumni.id
    assert queue_item.priority == 5
    assert queue_item.status == 'pending'
    assert queue_item.attempts == 0


def test_get_next_from_queue_priority_order(db_session):
    """Test that get_next_from_queue returns items in priority order."""
    # Create alumni
    alumni1 = create_alumni(db_session, name="Alumni 1", roll_number="TEST001")
    alumni2 = create_alumni(db_session, name="Alumni 2", roll_number="TEST002")
    alumni3 = create_alumni(db_session, name="Alumni 3", roll_number="TEST003")
    
    # Add to queue with different priorities
    add_to_scraping_queue(db_session, alumni1.id, priority=1)
    add_to_scraping_queue(db_session, alumni2.id, priority=10)  # Highest priority
    add_to_scraping_queue(db_session, alumni3.id, priority=5)
    
    # Get next should return highest priority
    next_item = get_next_from_queue(db_session)
    assert next_item.alumni_id == alumni2.id
    assert next_item.priority == 10


def test_get_next_from_queue_empty(db_session):
    """Test that get_next_from_queue returns None when queue is empty."""
    next_item = get_next_from_queue(db_session)
    assert next_item is None


def test_get_next_from_queue_only_pending(db_session):
    """Test that get_next_from_queue only returns pending items."""
    # Create alumni
    alumni1 = create_alumni(db_session, name="Alumni 1", roll_number="TEST001")
    alumni2 = create_alumni(db_session, name="Alumni 2", roll_number="TEST002")
    
    # Add to queue
    queue_item1 = add_to_scraping_queue(db_session, alumni1.id, priority=10)
    add_to_scraping_queue(db_session, alumni2.id, priority=5)
    
    # Mark first item as completed
    mark_queue_item_complete(db_session, queue_item1.id)
    
    # Get next should return the second item (only pending one)
    next_item = get_next_from_queue(db_session)
    assert next_item.alumni_id == alumni2.id


def test_mark_queue_item_complete(db_session):
    """Test marking a queue item as complete."""
    # Create alumni and add to queue
    alumni = create_alumni(db_session, name="Test Alumni", roll_number="TEST001")
    queue_item = add_to_scraping_queue(db_session, alumni.id)
    
    # Mark as complete
    result = mark_queue_item_complete(db_session, queue_item.id)
    assert result is True
    
    # Verify status changed
    db_session.refresh(queue_item)
    assert queue_item.status == 'completed'
    assert queue_item.last_attempt_at is not None


def test_mark_queue_item_failed(db_session):
    """Test marking a queue item as failed."""
    # Create alumni and add to queue
    alumni = create_alumni(db_session, name="Test Alumni", roll_number="TEST001")
    queue_item = add_to_scraping_queue(db_session, alumni.id)
    
    # Mark as failed
    result = mark_queue_item_failed(db_session, queue_item.id)
    assert result is True
    
    # Verify status changed and attempts incremented
    db_session.refresh(queue_item)
    assert queue_item.status == 'failed'
    assert queue_item.attempts == 1
    assert queue_item.last_attempt_at is not None


def test_mark_queue_item_in_progress(db_session):
    """Test marking a queue item as in progress."""
    # Create alumni and add to queue
    alumni = create_alumni(db_session, name="Test Alumni", roll_number="TEST001")
    queue_item = add_to_scraping_queue(db_session, alumni.id)
    
    # Mark as in progress
    result = mark_queue_item_in_progress(db_session, queue_item.id)
    assert result is True
    
    # Verify status changed and attempts incremented
    db_session.refresh(queue_item)
    assert queue_item.status == 'in_progress'
    assert queue_item.attempts == 1
    assert queue_item.last_attempt_at is not None


def test_mark_nonexistent_queue_item(db_session):
    """Test marking a nonexistent queue item returns False."""
    result = mark_queue_item_complete(db_session, 99999)
    assert result is False
    
    result = mark_queue_item_failed(db_session, 99999)
    assert result is False
    
    result = mark_queue_item_in_progress(db_session, 99999)
    assert result is False


def test_get_queue_statistics(db_session):
    """Test getting queue statistics."""
    # Create alumni
    alumni1 = create_alumni(db_session, name="Alumni 1", roll_number="TEST001")
    alumni2 = create_alumni(db_session, name="Alumni 2", roll_number="TEST002")
    alumni3 = create_alumni(db_session, name="Alumni 3", roll_number="TEST003")
    alumni4 = create_alumni(db_session, name="Alumni 4", roll_number="TEST004")
    
    # Add to queue with different statuses
    queue_item1 = add_to_scraping_queue(db_session, alumni1.id)  # pending
    queue_item2 = add_to_scraping_queue(db_session, alumni2.id)  # will be in_progress
    queue_item3 = add_to_scraping_queue(db_session, alumni3.id)  # will be completed
    queue_item4 = add_to_scraping_queue(db_session, alumni4.id)  # will be failed
    
    # Update statuses
    mark_queue_item_in_progress(db_session, queue_item2.id)
    mark_queue_item_complete(db_session, queue_item3.id)
    mark_queue_item_failed(db_session, queue_item4.id)
    
    # Get statistics
    stats = get_queue_statistics(db_session)
    
    # Verify
    assert stats['pending'] == 1
    assert stats['in_progress'] == 1
    assert stats['completed'] == 1
    assert stats['failed'] == 1
    assert stats['total'] == 4


def test_get_queue_statistics_empty(db_session):
    """Test getting queue statistics when queue is empty."""
    stats = get_queue_statistics(db_session)
    
    assert stats['pending'] == 0
    assert stats['in_progress'] == 0
    assert stats['completed'] == 0
    assert stats['failed'] == 0
    assert stats['total'] == 0


def test_queue_priority_with_same_priority(db_session):
    """Test that items with same priority are returned in FIFO order."""
    # Create alumni
    alumni1 = create_alumni(db_session, name="Alumni 1", roll_number="TEST001")
    alumni2 = create_alumni(db_session, name="Alumni 2", roll_number="TEST002")
    alumni3 = create_alumni(db_session, name="Alumni 3", roll_number="TEST003")
    
    # Add to queue with same priority (should be FIFO)
    add_to_scraping_queue(db_session, alumni1.id, priority=5)
    add_to_scraping_queue(db_session, alumni2.id, priority=5)
    add_to_scraping_queue(db_session, alumni3.id, priority=5)
    
    # Get next should return first added
    next_item = get_next_from_queue(db_session)
    assert next_item.alumni_id == alumni1.id
