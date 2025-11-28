"""
Integration tests for dashboard statistics.

Tests that the dashboard correctly displays statistics from the database.
"""

import uuid

import pytest

from alumni_system.database.crud import (
    create_alumni,
    get_alumni_count,
    get_unique_batches,
    get_unique_companies,
    get_unique_locations,
)


def test_dashboard_statistics_integration(db_session):
    """
    Test that dashboard statistics functions work correctly together.
    
    This test verifies that:
    - get_alumni_count returns accurate count
    - get_unique_batches returns correct unique batches
    - get_unique_companies returns correct unique companies
    - get_unique_locations returns correct unique locations
    """
    # Create test alumni with known data
    alumni_data = [
        {
            'roll_number': str(uuid.uuid4())[:20],
            'name': 'Alice Smith',
            'batch': '2020',
            'current_company': 'Google',
            'location': 'Bangalore'
        },
        {
            'roll_number': str(uuid.uuid4())[:20],
            'name': 'Bob Jones',
            'batch': '2020',
            'current_company': 'Microsoft',
            'location': 'Mumbai'
        },
        {
            'roll_number': str(uuid.uuid4())[:20],
            'name': 'Charlie Brown',
            'batch': '2021',
            'current_company': 'Google',
            'location': 'Bangalore'
        },
        {
            'roll_number': str(uuid.uuid4())[:20],
            'name': 'Diana Prince',
            'batch': '2021',
            'current_company': 'Amazon',
            'location': 'Delhi'
        },
    ]
    
    # Create alumni
    for data in alumni_data:
        create_alumni(db_session, **data)
    
    # Test count
    count = get_alumni_count(db_session)
    assert count == 4, f"Expected 4 alumni, got {count}"
    
    # Test unique batches
    batches = get_unique_batches(db_session)
    assert len(batches) == 2, f"Expected 2 unique batches, got {len(batches)}"
    assert set(batches) == {'2020', '2021'}, f"Expected batches 2020 and 2021, got {batches}"
    
    # Test unique companies
    companies = get_unique_companies(db_session)
    assert len(companies) == 3, f"Expected 3 unique companies, got {len(companies)}"
    assert set(companies) == {'Google', 'Microsoft', 'Amazon'}, f"Expected Google, Microsoft, Amazon, got {companies}"
    
    # Test unique locations
    locations = get_unique_locations(db_session)
    assert len(locations) == 3, f"Expected 3 unique locations, got {len(locations)}"
    assert set(locations) == {'Bangalore', 'Mumbai', 'Delhi'}, f"Expected Bangalore, Mumbai, Delhi, got {locations}"


def test_dashboard_statistics_with_empty_database(db_session):
    """
    Test that dashboard statistics work correctly with an empty database.
    """
    # Test count
    count = get_alumni_count(db_session)
    assert count == 0, f"Expected 0 alumni in empty database, got {count}"
    
    # Test unique batches
    batches = get_unique_batches(db_session)
    assert len(batches) == 0, f"Expected 0 unique batches in empty database, got {len(batches)}"
    
    # Test unique companies
    companies = get_unique_companies(db_session)
    assert len(companies) == 0, f"Expected 0 unique companies in empty database, got {len(companies)}"
    
    # Test unique locations
    locations = get_unique_locations(db_session)
    assert len(locations) == 0, f"Expected 0 unique locations in empty database, got {len(locations)}"


def test_dashboard_statistics_with_null_values(db_session):
    """
    Test that dashboard statistics handle null values correctly.
    """
    # Create alumni with some null values
    alumni_data = [
        {
            'roll_number': str(uuid.uuid4())[:20],
            'name': 'Alice Smith',
            'batch': '2020',
            'current_company': 'Google',
            'location': 'Bangalore'
        },
        {
            'roll_number': str(uuid.uuid4())[:20],
            'name': 'Bob Jones',
            'batch': '2020',
            'current_company': None,  # No company
            'location': None  # No location
        },
        {
            'roll_number': str(uuid.uuid4())[:20],
            'name': 'Charlie Brown',
            'batch': None,  # No batch
            'current_company': 'Microsoft',
            'location': 'Mumbai'
        },
    ]
    
    # Create alumni
    for data in alumni_data:
        create_alumni(db_session, **data)
    
    # Test count (should count all alumni regardless of null values)
    count = get_alumni_count(db_session)
    assert count == 3, f"Expected 3 alumni, got {count}"
    
    # Test unique batches (should only count non-null batches)
    batches = get_unique_batches(db_session)
    assert len(batches) == 1, f"Expected 1 unique batch, got {len(batches)}"
    assert '2020' in batches, f"Expected batch 2020, got {batches}"
    
    # Test unique companies (should only count non-null companies)
    companies = get_unique_companies(db_session)
    assert len(companies) == 2, f"Expected 2 unique companies, got {len(companies)}"
    assert set(companies) == {'Google', 'Microsoft'}, f"Expected Google and Microsoft, got {companies}"
    
    # Test unique locations (should only count non-null locations)
    locations = get_unique_locations(db_session)
    assert len(locations) == 2, f"Expected 2 unique locations, got {len(locations)}"
    assert set(locations) == {'Bangalore', 'Mumbai'}, f"Expected Bangalore and Mumbai, got {locations}"
