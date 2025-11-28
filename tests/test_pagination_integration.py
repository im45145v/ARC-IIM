"""
Integration tests for pagination functionality in the frontend.

Tests that the pagination implementation correctly integrates with the database
and follows the pagination math properties.
"""

import math

import pytest
from sqlalchemy.orm import Session

from alumni_system.database.crud import create_alumni, get_all_alumni, get_alumni_count
from alumni_system.database.models import Alumni


def test_pagination_with_database(db_session: Session):
    """
    Test pagination integration with actual database operations.
    
    Verifies that:
    - Total count is accurate
    - Pages contain correct number of records
    - All records are accessible through pagination
    - No duplicates or gaps
    """
    # Create test alumni records
    num_records = 127  # Intentionally not a multiple of common page sizes
    created_ids = []
    
    for i in range(num_records):
        alumni = create_alumni(
            db_session,
            name=f"Test Alumni {i}",
            roll_number=f"TEST{i:04d}",
            batch="2020"
        )
        created_ids.append(alumni.id)
    
    # Test with different page sizes
    for page_size in [25, 50, 100]:
        # Calculate expected total pages
        total_count = get_alumni_count(db_session)
        assert total_count == num_records, f"Total count should be {num_records}"
        
        total_pages = math.ceil(total_count / page_size)
        
        # Verify we can access all records through pagination
        all_paginated_ids = []
        
        for page_num in range(1, total_pages + 1):
            skip = (page_num - 1) * page_size
            page_records = get_all_alumni(db_session, skip=skip, limit=page_size)
            
            # Verify page size (except possibly last page)
            if page_num < total_pages:
                assert len(page_records) == page_size, \
                    f"Page {page_num} should have {page_size} records, but has {len(page_records)}"
            else:
                # Last page should have remaining records
                expected_last_page_size = total_count - (total_pages - 1) * page_size
                assert len(page_records) == expected_last_page_size, \
                    f"Last page should have {expected_last_page_size} records, but has {len(page_records)}"
            
            # Collect IDs from this page
            page_ids = [alumni.id for alumni in page_records]
            all_paginated_ids.extend(page_ids)
        
        # Verify all records were accessed exactly once
        assert len(all_paginated_ids) == num_records, \
            f"Should access all {num_records} records, but got {len(all_paginated_ids)}"
        
        assert len(set(all_paginated_ids)) == num_records, \
            f"Should have no duplicates, but got {len(all_paginated_ids) - len(set(all_paginated_ids))} duplicates"
        
        assert set(all_paginated_ids) == set(created_ids), \
            "Paginated IDs should match created IDs"


def test_pagination_edge_cases(db_session: Session):
    """
    Test pagination edge cases.
    
    Verifies:
    - Empty database (0 records)
    - Single record
    - Exact multiple of page size
    - Page size larger than total records
    """
    # Test 1: Empty database
    total_count = get_alumni_count(db_session)
    assert total_count == 0
    
    total_pages = math.ceil(total_count / 25) if total_count > 0 else 0
    assert total_pages == 0
    
    records = get_all_alumni(db_session, skip=0, limit=25)
    assert len(records) == 0
    
    # Test 2: Single record
    alumni1 = create_alumni(db_session, name="Single Alumni", roll_number="SINGLE001")
    
    total_count = get_alumni_count(db_session)
    assert total_count == 1
    
    total_pages = math.ceil(total_count / 25)
    assert total_pages == 1
    
    records = get_all_alumni(db_session, skip=0, limit=25)
    assert len(records) == 1
    assert records[0].id == alumni1.id
    
    # Test 3: Exact multiple of page size (50 records, page size 25)
    for i in range(49):  # Already have 1, need 49 more for 50 total
        create_alumni(db_session, name=f"Alumni {i}", roll_number=f"MULTI{i:04d}")
    
    total_count = get_alumni_count(db_session)
    assert total_count == 50
    
    page_size = 25
    total_pages = math.ceil(total_count / page_size)
    assert total_pages == 2
    
    # First page should have exactly 25
    page1 = get_all_alumni(db_session, skip=0, limit=page_size)
    assert len(page1) == 25
    
    # Second page should have exactly 25
    page2 = get_all_alumni(db_session, skip=25, limit=page_size)
    assert len(page2) == 25
    
    # Test 4: Page size larger than total records
    total_count = get_alumni_count(db_session)
    page_size = 100
    
    total_pages = math.ceil(total_count / page_size)
    assert total_pages == 1
    
    records = get_all_alumni(db_session, skip=0, limit=page_size)
    assert len(records) == total_count


def test_pagination_consistency(db_session: Session):
    """
    Test that pagination is consistent across multiple queries.
    
    Verifies that requesting the same page multiple times returns the same results.
    """
    # Create test records
    for i in range(75):
        create_alumni(db_session, name=f"Alumni {i}", roll_number=f"CONS{i:04d}")
    
    page_size = 25
    page_num = 2
    skip = (page_num - 1) * page_size
    
    # Query the same page multiple times
    results1 = get_all_alumni(db_session, skip=skip, limit=page_size)
    results2 = get_all_alumni(db_session, skip=skip, limit=page_size)
    results3 = get_all_alumni(db_session, skip=skip, limit=page_size)
    
    # All queries should return the same records
    ids1 = [a.id for a in results1]
    ids2 = [a.id for a in results2]
    ids3 = [a.id for a in results3]
    
    assert ids1 == ids2 == ids3, "Pagination should be consistent across queries"
    assert len(ids1) == page_size, f"Should return {page_size} records"


def test_pagination_boundary_values(db_session: Session):
    """
    Test pagination with boundary values.
    
    Verifies correct behavior at page boundaries.
    """
    # Create 100 records
    for i in range(100):
        create_alumni(db_session, name=f"Alumni {i}", roll_number=f"BOUND{i:04d}")
    
    total_count = get_alumni_count(db_session)
    page_size = 25
    total_pages = math.ceil(total_count / page_size)
    
    # Test first page (page 1)
    page1 = get_all_alumni(db_session, skip=0, limit=page_size)
    assert len(page1) == page_size
    
    # Test last page (page 4)
    skip_last = (total_pages - 1) * page_size
    page_last = get_all_alumni(db_session, skip=skip_last, limit=page_size)
    assert len(page_last) == page_size  # 100 is exactly divisible by 25
    
    # Test beyond last page (should return empty)
    skip_beyond = total_pages * page_size
    page_beyond = get_all_alumni(db_session, skip=skip_beyond, limit=page_size)
    assert len(page_beyond) == 0, "Requesting page beyond last should return empty"


def test_pagination_with_filters(db_session: Session):
    """
    Test that pagination works correctly with filters.
    
    Note: This is a basic test. Full filter integration is tested elsewhere.
    """
    # Create records with different batches
    for i in range(30):
        batch = "2020" if i < 15 else "2021"
        create_alumni(db_session, name=f"Alumni {i}", roll_number=f"FILT{i:04d}", batch=batch)
    
    # Get all records for batch 2020 with pagination
    page_size = 10
    
    # Page 1
    page1 = get_all_alumni(db_session, skip=0, limit=page_size, batch="2020")
    assert len(page1) == 10
    assert all(a.batch == "2020" for a in page1)
    
    # Page 2
    page2 = get_all_alumni(db_session, skip=10, limit=page_size, batch="2020")
    assert len(page2) == 5  # Only 15 total in batch 2020
    assert all(a.batch == "2020" for a in page2)
