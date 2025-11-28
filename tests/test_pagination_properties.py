"""
Property-based tests for pagination functionality.

Tests pagination math correctness across various inputs.
"""

import math

from hypothesis import given, strategies as st


def calculate_total_pages(total_records: int, page_size: int) -> int:
    """
    Calculate the total number of pages needed for pagination.
    
    Args:
        total_records: Total number of records
        page_size: Number of records per page
        
    Returns:
        Total number of pages (ceiling of total_records / page_size)
    """
    if page_size <= 0:
        raise ValueError("Page size must be positive")
    if total_records < 0:
        raise ValueError("Total records cannot be negative")
    
    if total_records == 0:
        return 0
    
    return math.ceil(total_records / page_size)


def get_page_records(total_records: int, page_num: int, page_size: int) -> tuple[int, int]:
    """
    Calculate the start and end indices for a given page.
    
    Args:
        total_records: Total number of records
        page_num: Page number (1-indexed)
        page_size: Number of records per page
        
    Returns:
        Tuple of (start_index, end_index) for slicing
    """
    if page_size <= 0:
        raise ValueError("Page size must be positive")
    if page_num < 1:
        raise ValueError("Page number must be at least 1")
    if total_records < 0:
        raise ValueError("Total records cannot be negative")
    
    start_index = (page_num - 1) * page_size
    end_index = min(start_index + page_size, total_records)
    
    return start_index, end_index


# =============================================================================
# PROPERTY-BASED TESTS
# =============================================================================

@given(
    total_records=st.integers(min_value=0, max_value=10000),
    page_size=st.integers(min_value=1, max_value=100)
)
def test_pagination_math_is_correct(total_records: int, page_size: int):
    """
    **Feature: alumni-management-system, Property 25: Pagination math is correct**
    **Validates: Requirements 4.2**
    
    For any N total records with page size P, the number of pages should be ceil(N/P).
    
    This property verifies that:
    1. The total pages calculation matches ceil(total_records / page_size)
    2. All records can be accessed through pagination
    3. No records are duplicated or skipped
    4. The last page contains the remaining records
    """
    # Calculate total pages
    total_pages = calculate_total_pages(total_records, page_size)
    
    # Property 1: Total pages should equal ceil(total_records / page_size)
    expected_pages = math.ceil(total_records / page_size) if total_records > 0 else 0
    assert total_pages == expected_pages, \
        f"Total pages {total_pages} != expected {expected_pages} for {total_records} records with page size {page_size}"
    
    # Property 2: If there are records, there should be at least 1 page
    if total_records > 0:
        assert total_pages >= 1, \
            f"Should have at least 1 page for {total_records} records"
    else:
        assert total_pages == 0, \
            f"Should have 0 pages for 0 records"
    
    # Property 3: All pages except possibly the last should be full
    if total_pages > 0:
        for page_num in range(1, total_pages + 1):
            start_idx, end_idx = get_page_records(total_records, page_num, page_size)
            records_on_page = end_idx - start_idx
            
            if page_num < total_pages:
                # All pages before the last should be full
                assert records_on_page == page_size, \
                    f"Page {page_num} should have {page_size} records, but has {records_on_page}"
            else:
                # Last page should have remaining records (1 to page_size)
                expected_last_page_size = total_records - (total_pages - 1) * page_size
                assert records_on_page == expected_last_page_size, \
                    f"Last page should have {expected_last_page_size} records, but has {records_on_page}"
                assert 1 <= records_on_page <= page_size, \
                    f"Last page should have between 1 and {page_size} records, but has {records_on_page}"
    
    # Property 4: Total records across all pages should equal total_records
    if total_pages > 0:
        total_covered = 0
        for page_num in range(1, total_pages + 1):
            start_idx, end_idx = get_page_records(total_records, page_num, page_size)
            total_covered += (end_idx - start_idx)
        
        assert total_covered == total_records, \
            f"Total records covered {total_covered} != total records {total_records}"
    
    # Property 5: No gaps or overlaps between pages
    if total_pages > 1:
        for page_num in range(1, total_pages):
            _, end_idx_current = get_page_records(total_records, page_num, page_size)
            start_idx_next, _ = get_page_records(total_records, page_num + 1, page_size)
            
            assert end_idx_current == start_idx_next, \
                f"Gap or overlap between page {page_num} and {page_num + 1}: " \
                f"end of page {page_num} is {end_idx_current}, start of page {page_num + 1} is {start_idx_next}"


@given(
    total_records=st.integers(min_value=1, max_value=10000),
    page_size=st.integers(min_value=1, max_value=100)
)
def test_pagination_boundary_conditions(total_records: int, page_size: int):
    """
    Test boundary conditions for pagination.
    
    Verifies that:
    - First page starts at index 0
    - Last page ends at total_records
    - Page indices are always within valid range
    """
    total_pages = calculate_total_pages(total_records, page_size)
    
    # First page should start at 0
    start_idx, _ = get_page_records(total_records, 1, page_size)
    assert start_idx == 0, f"First page should start at index 0, but starts at {start_idx}"
    
    # Last page should end at total_records
    if total_pages > 0:
        _, end_idx = get_page_records(total_records, total_pages, page_size)
        assert end_idx == total_records, \
            f"Last page should end at {total_records}, but ends at {end_idx}"
    
    # All page indices should be within [0, total_records]
    for page_num in range(1, total_pages + 1):
        start_idx, end_idx = get_page_records(total_records, page_num, page_size)
        assert 0 <= start_idx <= total_records, \
            f"Start index {start_idx} out of range [0, {total_records}]"
        assert 0 <= end_idx <= total_records, \
            f"End index {end_idx} out of range [0, {total_records}]"
        assert start_idx <= end_idx, \
            f"Start index {start_idx} should be <= end index {end_idx}"


@given(
    page_size=st.integers(min_value=1, max_value=100)
)
def test_pagination_with_zero_records(page_size: int):
    """
    Test pagination with zero records.
    
    Verifies that pagination handles empty datasets correctly.
    """
    total_pages = calculate_total_pages(0, page_size)
    assert total_pages == 0, f"Should have 0 pages for 0 records, but got {total_pages}"


@given(
    total_records=st.integers(min_value=1, max_value=10000)
)
def test_pagination_with_page_size_one(total_records: int):
    """
    Test pagination with page size of 1.
    
    Verifies that with page size 1, total pages equals total records.
    """
    page_size = 1
    total_pages = calculate_total_pages(total_records, page_size)
    assert total_pages == total_records, \
        f"With page size 1, total pages {total_pages} should equal total records {total_records}"


@given(
    total_records=st.integers(min_value=1, max_value=10000),
    page_size=st.integers(min_value=1, max_value=100)
)
def test_pagination_page_size_larger_than_total(total_records: int, page_size: int):
    """
    Test pagination when page size is larger than total records.
    
    Verifies that when page_size >= total_records, we get exactly 1 page.
    """
    if page_size >= total_records:
        total_pages = calculate_total_pages(total_records, page_size)
        assert total_pages == 1, \
            f"When page size {page_size} >= total records {total_records}, should have 1 page, but got {total_pages}"
        
        start_idx, end_idx = get_page_records(total_records, 1, page_size)
        assert start_idx == 0 and end_idx == total_records, \
            f"Single page should contain all records [0, {total_records}], but got [{start_idx}, {end_idx}]"
