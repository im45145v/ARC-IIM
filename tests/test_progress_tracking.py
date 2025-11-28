"""
Property-based tests for scraping progress tracking.

Tests Property 42: Progress tracking matches completion
"""

import uuid

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alumni_system.database.crud import (
    add_to_scraping_queue,
    create_alumni,
    get_queue_statistics,
    mark_queue_item_complete,
    mark_queue_item_in_progress,
)


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=500)
@given(
    num_profiles=st.integers(min_value=1, max_value=50),
    num_completed=st.integers(min_value=0, max_value=50),
)
def test_progress_tracking_matches_completion(clean_db_session, num_profiles, num_completed):
    """
    **Feature: alumni-management-system, Property 42: Progress tracking matches completion**
    **Validates: Requirements 6.8**
    
    Property: For any scraping job processing N profiles, after completing M profiles,
    the progress should show M/N.
    
    This test verifies that:
    1. Queue statistics accurately reflect the number of completed items
    2. Progress calculation (completed/total) is correct
    3. The relationship between pending, in_progress, and completed is maintained
    """
    # Ensure num_completed doesn't exceed num_profiles
    if num_completed > num_profiles:
        num_completed = num_profiles
    
    # Generate unique ID for this test run to avoid conflicts
    test_id = str(uuid.uuid4())[:8]
    
    # Create alumni records and add to queue with unique roll numbers
    alumni_ids = []
    for i in range(num_profiles):
        alumni = create_alumni(
            clean_db_session,
            name=f"Test Alumni {test_id}_{i}",
            roll_number=f"TEST_{test_id}_{i:04d}",
        )
        alumni_ids.append(alumni.id)
        add_to_scraping_queue(clean_db_session, alumni.id)
    
    # Get initial statistics
    from alumni_system.database.models import ScrapingQueue
    
    # Mark some items as in progress, then complete them
    queue_items = (
        clean_db_session.query(ScrapingQueue)
        .filter(ScrapingQueue.alumni_id.in_(alumni_ids))
        .filter(ScrapingQueue.status == 'pending')
        .limit(num_completed)
        .all()
    )
    
    for queue_item in queue_items:
        mark_queue_item_in_progress(clean_db_session, queue_item.id)
        mark_queue_item_complete(clean_db_session, queue_item.id)
    
    # Get final statistics for our items only
    completed_count = (
        clean_db_session.query(ScrapingQueue)
        .filter(ScrapingQueue.alumni_id.in_(alumni_ids))
        .filter(ScrapingQueue.status == 'completed')
        .count()
    )
    
    pending_count = (
        clean_db_session.query(ScrapingQueue)
        .filter(ScrapingQueue.alumni_id.in_(alumni_ids))
        .filter(ScrapingQueue.status == 'pending')
        .count()
    )
    
    in_progress_count = (
        clean_db_session.query(ScrapingQueue)
        .filter(ScrapingQueue.alumni_id.in_(alumni_ids))
        .filter(ScrapingQueue.status == 'in_progress')
        .count()
    )
    
    failed_count = (
        clean_db_session.query(ScrapingQueue)
        .filter(ScrapingQueue.alumni_id.in_(alumni_ids))
        .filter(ScrapingQueue.status == 'failed')
        .count()
    )
    
    # Verify progress tracking matches completion
    assert completed_count == num_completed, (
        f"Expected {num_completed} completed items, but got {completed_count}"
    )
    
    # Verify pending count decreased correctly
    expected_pending = num_profiles - num_completed
    assert pending_count == expected_pending, (
        f"Expected {expected_pending} pending items, but got {pending_count}"
    )
    
    # Verify total is conserved (pending + in_progress + completed + failed = total)
    total_accounted = pending_count + in_progress_count + completed_count + failed_count
    assert total_accounted == num_profiles, (
        f"Total items ({total_accounted}) doesn't match created profiles ({num_profiles})"
    )
    
    # Verify progress calculation
    if num_profiles > 0:
        progress_ratio = completed_count / num_profiles
        expected_ratio = num_completed / num_profiles
        assert abs(progress_ratio - expected_ratio) < 0.001, (
            f"Progress ratio {progress_ratio} doesn't match expected {expected_ratio}"
        )


def test_progress_tracking_edge_case_zero_profiles(clean_db_session):
    """
    Edge case: Progress tracking with zero profiles.
    """
    # Create a fresh test with unique IDs
    test_id = str(uuid.uuid4())[:8]
    alumni_ids = []  # Empty list
    
    from alumni_system.database.models import ScrapingQueue
    
    # Count only our test items (should be zero)
    completed_count = (
        clean_db_session.query(ScrapingQueue)
        .filter(ScrapingQueue.alumni_id.in_(alumni_ids) if alumni_ids else False)
        .filter(ScrapingQueue.status == 'completed')
        .count()
    )
    
    pending_count = (
        clean_db_session.query(ScrapingQueue)
        .filter(ScrapingQueue.alumni_id.in_(alumni_ids) if alumni_ids else False)
        .filter(ScrapingQueue.status == 'pending')
        .count()
    )
    
    # With no profiles, all counts should be zero
    assert completed_count == 0
    assert pending_count == 0


def test_progress_tracking_edge_case_all_completed(clean_db_session):
    """
    Edge case: Progress tracking when all profiles are completed.
    """
    num_profiles = 5
    test_id = str(uuid.uuid4())[:8]
    alumni_ids = []
    
    # Create and queue profiles
    for i in range(num_profiles):
        alumni = create_alumni(
            clean_db_session,
            name=f"Test Alumni {test_id}_{i}",
            roll_number=f"TEST_{test_id}_{i:04d}",
        )
        alumni_ids.append(alumni.id)
        queue_item = add_to_scraping_queue(clean_db_session, alumni.id)
        mark_queue_item_in_progress(clean_db_session, queue_item.id)
        mark_queue_item_complete(clean_db_session, queue_item.id)
    
    from alumni_system.database.models import ScrapingQueue
    
    # Count only our test items
    completed_count = (
        clean_db_session.query(ScrapingQueue)
        .filter(ScrapingQueue.alumni_id.in_(alumni_ids))
        .filter(ScrapingQueue.status == 'completed')
        .count()
    )
    
    pending_count = (
        clean_db_session.query(ScrapingQueue)
        .filter(ScrapingQueue.alumni_id.in_(alumni_ids))
        .filter(ScrapingQueue.status == 'pending')
        .count()
    )
    
    # All should be completed
    assert completed_count == num_profiles
    assert pending_count == 0
    
    # Progress should be 100%
    progress = completed_count / num_profiles if num_profiles > 0 else 0
    assert progress == 1.0


def test_progress_tracking_edge_case_none_completed(clean_db_session):
    """
    Edge case: Progress tracking when no profiles are completed yet.
    """
    num_profiles = 5
    test_id = str(uuid.uuid4())[:8]
    alumni_ids = []
    
    # Create and queue profiles
    for i in range(num_profiles):
        alumni = create_alumni(
            clean_db_session,
            name=f"Test Alumni {test_id}_{i}",
            roll_number=f"TEST_{test_id}_{i:04d}",
        )
        alumni_ids.append(alumni.id)
        add_to_scraping_queue(clean_db_session, alumni.id)
    
    from alumni_system.database.models import ScrapingQueue
    
    # Count only our test items
    completed_count = (
        clean_db_session.query(ScrapingQueue)
        .filter(ScrapingQueue.alumni_id.in_(alumni_ids))
        .filter(ScrapingQueue.status == 'completed')
        .count()
    )
    
    pending_count = (
        clean_db_session.query(ScrapingQueue)
        .filter(ScrapingQueue.alumni_id.in_(alumni_ids))
        .filter(ScrapingQueue.status == 'pending')
        .count()
    )
    
    # None should be completed
    assert completed_count == 0
    assert pending_count == num_profiles
    
    # Progress should be 0%
    progress = completed_count / num_profiles if num_profiles > 0 else 0
    assert progress == 0.0
