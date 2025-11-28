"""
Property-based tests for dashboard statistics.

Tests correctness properties for dashboard statistics display including:
- Dashboard statistics match database counts
"""

import uuid

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alumni_system.database.crud import (
    create_alumni,
    get_all_alumni,
    get_unique_batches,
    get_unique_companies,
    get_unique_locations,
)


# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def alumni_data(draw):
    """Generate random alumni data with unique roll number."""
    return {
        'roll_number': str(uuid.uuid4())[:20],  # Ensure unique roll numbers
        'name': draw(st.text(min_size=3, max_size=50, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ')),
        'batch': draw(st.one_of(st.just('2020'), st.just('2021'), st.just('2022'), st.just('2023'))),
        'current_company': draw(st.one_of(st.just('Google'), st.just('Microsoft'), st.just('Amazon'), st.just('Apple'), st.none())),
        'current_designation': draw(st.text(min_size=3, max_size=50, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ')),
        'location': draw(st.one_of(st.just('Bangalore'), st.just('Mumbai'), st.just('Delhi'), st.just('Hyderabad'), st.none())),
    }


@st.composite
def alumni_list_data(draw):
    """Generate a list of alumni data with unique roll numbers."""
    num_alumni = draw(st.integers(min_value=1, max_value=20))
    return [draw(alumni_data()) for _ in range(num_alumni)]


# =============================================================================
# Property Tests
# =============================================================================


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=500)
@given(alumni_list=alumni_list_data())
def test_property_24_dashboard_statistics_match_database_counts(db_session, alumni_list):
    """
    **Feature: alumni-management-system, Property 24: Dashboard statistics match database counts**
    **Validates: Requirements 4.1**
    
    For any database state, the dashboard should display counts that exactly match 
    the actual number of alumni, batches, companies, and locations in the database.
    """
    # Get initial counts before creating new alumni
    initial_alumni = get_all_alumni(db_session, limit=10000)
    initial_count = len(initial_alumni)
    
    # Create alumni records
    created_alumni = []
    for alumni_data_item in alumni_list:
        try:
            alumni = create_alumni(db_session, **alumni_data_item)
            created_alumni.append(alumni)
        except Exception:
            # Skip duplicates or invalid data
            pass
    
    # Get dashboard statistics (simulating what the dashboard would display)
    all_alumni = get_all_alumni(db_session, limit=10000)
    total_alumni_count = len(all_alumni)
    
    unique_batches = get_unique_batches(db_session)
    unique_companies = get_unique_companies(db_session)
    unique_locations = get_unique_locations(db_session)
    
    # Verify counts match actual database state
    # Total alumni count should match initial + created
    expected_total = initial_count + len(created_alumni)
    assert total_alumni_count == expected_total, \
        f"Dashboard alumni count {total_alumni_count} should match expected count {expected_total} (initial {initial_count} + created {len(created_alumni)})"
    
    # Unique batches count should match all alumni in database
    expected_batches = set()
    for alumni in all_alumni:
        if alumni.batch:
            expected_batches.add(alumni.batch)
    
    assert len(unique_batches) == len(expected_batches), \
        f"Dashboard batch count {len(unique_batches)} should match actual unique batches {len(expected_batches)}"
    
    # Verify all expected batches are present
    assert set(unique_batches) == expected_batches, \
        f"Dashboard batches {set(unique_batches)} should match expected batches {expected_batches}"
    
    # Unique companies count should match all alumni in database
    expected_companies = set()
    for alumni in all_alumni:
        if alumni.current_company:
            expected_companies.add(alumni.current_company)
    
    assert len(unique_companies) == len(expected_companies), \
        f"Dashboard company count {len(unique_companies)} should match actual unique companies {len(expected_companies)}"
    
    # Verify all expected companies are present
    assert set(unique_companies) == expected_companies, \
        f"Dashboard companies {set(unique_companies)} should match expected companies {expected_companies}"
    
    # Unique locations count should match all alumni in database
    expected_locations = set()
    for alumni in all_alumni:
        if alumni.location:
            expected_locations.add(alumni.location)
    
    assert len(unique_locations) == len(expected_locations), \
        f"Dashboard location count {len(unique_locations)} should match actual unique locations {len(expected_locations)}"
    
    # Verify all expected locations are present
    assert set(unique_locations) == expected_locations, \
        f"Dashboard locations {set(unique_locations)} should match expected locations {expected_locations}"
