"""
Property-based tests for bulk import functionality.

Tests the import utilities for flexible column detection, duplicate handling,
LinkedIn URL conversion, queue population, and import summary accuracy.
"""

import time
import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alumni_system.database.crud import (
    get_alumni_by_roll_number,
    get_queue_statistics,
)
from alumni_system.database.import_utils import (
    detect_columns,
    import_from_dataframe,
    normalize_linkedin_url,
)

# Global counter to ensure uniqueness across hypothesis examples
_test_counter = 0

def get_unique_id():
    """Get a unique ID for test data."""
    global _test_counter
    _test_counter += 1
    return f"{int(time.time() * 1000000)}_{_test_counter}"


# =============================================================================
# Property 37: Column name detection is flexible
# Feature: alumni-management-system, Property 37: Column name detection is flexible
# Validates: Requirements 6.1
# =============================================================================


@given(
    roll_col=st.sampled_from([
        'Roll No.', 'roll_number', 'Roll Number', 'rollno', 'roll',
        'Roll No', 'ROLL NO', 'Roll_Number'
    ]),
    name_col=st.sampled_from([
        'Name of the Student', 'Name', 'name', 'Student Name',
        'NAME', 'Student_Name'
    ]),
    linkedin_col=st.sampled_from([
        'LinkedIn ID', 'linkedin_url', 'Linkedin ID', 'LinkedIn',
        'LINKEDIN ID', 'LinkedIn_ID', 'linkedin_id'
    ])
)
@settings(max_examples=100)
def test_property_37_column_name_detection_is_flexible(
    roll_col: str,
    name_col: str,
    linkedin_col: str
):
    """
    Property 37: Column name detection is flexible.
    
    For any Excel/CSV file with columns matching common variations
    (e.g., "Roll No.", "roll_number", "Roll Number"), the system should
    correctly identify and map all required columns.
    
    **Validates: Requirements 6.1**
    """
    # Create a DataFrame with various column name formats
    df = pd.DataFrame({
        roll_col: ['2020001', '2020002'],
        name_col: ['Alice', 'Bob'],
        linkedin_col: ['alice123', 'bob456']
    })
    
    # Detect columns
    detected = detect_columns(df)
    
    # Verify that all columns were correctly mapped to database fields
    assert 'roll_number' in detected
    assert detected['roll_number'] == roll_col
    
    assert 'name' in detected
    assert detected['name'] == name_col
    
    assert 'linkedin_id' in detected
    assert detected['linkedin_id'] == linkedin_col


# =============================================================================
# Property 38: Import creates correct number of records
# Feature: alumni-management-system, Property 38: Import creates correct number of records
# Validates: Requirements 6.2
# =============================================================================


@given(
    num_records=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_38_import_creates_correct_number_of_records(
    db_session,
    num_records: int
):
    """
    Property 38: Import creates correct number of records.
    
    For any Excel/CSV file with N valid rows, importing should result
    in exactly N alumni records being created or updated.
    
    **Validates: Requirements 6.2**
    """
    # Create a DataFrame with N valid rows (use unique ID to ensure no collisions)
    unique_id = get_unique_id()
    data = {
        'Roll No.': [f'R{unique_id}_{str(i).zfill(3)}' for i in range(num_records)],
        'Name': [f'Student_{unique_id}_{i}' for i in range(num_records)],
        'LinkedIn ID': [f'student{unique_id}_{i}' for i in range(num_records)]
    }
    df = pd.DataFrame(data)
    
    # Import the data
    summary = import_from_dataframe(
        db_session,
        df,
        queue_for_scraping=False,
        skip_duplicates=True
    )
    
    # Verify that exactly N records were created
    assert summary.new_records == num_records
    assert summary.updated_records == 0
    assert summary.skipped_records == 0
    assert summary.total_rows == num_records


# =============================================================================
# Property 39: LinkedIn username conversion is consistent
# Feature: alumni-management-system, Property 39: LinkedIn username conversion is consistent
# Validates: Requirements 6.3
# =============================================================================


@given(
    username=st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='-_'),
        min_size=3,
        max_size=30
    ).filter(lambda x: x and x.strip() and not x.startswith('-') and not x.endswith('-'))
)
@settings(max_examples=100)
def test_property_39_linkedin_username_conversion_is_consistent(username: str):
    """
    Property 39: LinkedIn username conversion is consistent.
    
    For any LinkedIn username U (without https://), the system should
    convert it to "https://www.linkedin.com/in/U".
    
    **Validates: Requirements 6.3**
    """
    # Convert username to URL
    linkedin_url, linkedin_id = normalize_linkedin_url(username)
    
    # Verify the conversion is consistent
    assert linkedin_url == f"https://www.linkedin.com/in/{username}"
    assert linkedin_id == username


@given(
    username=st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='-_'),
        min_size=3,
        max_size=30
    ).filter(lambda x: x and x.strip() and not x.startswith('-') and not x.endswith('-'))
)
@settings(max_examples=100)
def test_property_39_linkedin_url_extraction_is_consistent(username: str):
    """
    Property 39 (variant): LinkedIn URL extraction is consistent.
    
    For any full LinkedIn URL, the system should correctly extract
    the username/ID.
    
    **Validates: Requirements 6.3**
    """
    # Create a full URL
    full_url = f"https://www.linkedin.com/in/{username}"
    
    # Extract ID from URL
    linkedin_url, linkedin_id = normalize_linkedin_url(full_url)
    
    # Verify the extraction is consistent
    assert linkedin_url == full_url
    assert linkedin_id == username


# =============================================================================
# Property 40: Import queues all profiles
# Feature: alumni-management-system, Property 40: Import queues all profiles
# Validates: Requirements 6.4
# =============================================================================


@given(
    num_records=st.integers(min_value=1, max_value=15)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_40_import_queues_all_profiles(
    db_session,
    num_records: int
):
    """
    Property 40: Import queues all profiles.
    
    For any import of N alumni records, exactly N entries should be
    added to the scraping queue.
    
    **Validates: Requirements 6.4**
    """
    # Get initial queue stats
    initial_stats = get_queue_statistics(db_session)
    initial_pending = initial_stats['pending']
    
    # Create a DataFrame with N records (all with LinkedIn URLs, use unique ID)
    unique_id = get_unique_id()
    data = {
        'Roll No.': [f'Q{unique_id}_{str(i).zfill(3)}' for i in range(num_records)],
        'Name': [f'Student_{unique_id}_{i}' for i in range(num_records)],
        'LinkedIn ID': [f'qstudent{unique_id}_{i}' for i in range(num_records)]
    }
    df = pd.DataFrame(data)
    
    # Import with queue_for_scraping=True
    summary = import_from_dataframe(
        db_session,
        df,
        queue_for_scraping=True,
        skip_duplicates=True
    )
    
    # Get final queue stats
    final_stats = get_queue_statistics(db_session)
    final_pending = final_stats['pending']
    
    # Verify that exactly N profiles were queued
    assert summary.queued_for_scraping == num_records
    assert final_pending - initial_pending == num_records


# =============================================================================
# Property 41: Duplicate roll numbers are skipped
# Feature: alumni-management-system, Property 41: Duplicate roll numbers are skipped
# Validates: Requirements 6.5
# =============================================================================


@given(
    num_duplicates=st.integers(min_value=2, max_value=10)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_41_duplicate_roll_numbers_are_skipped(
    db_session,
    num_duplicates: int
):
    """
    Property 41: Duplicate roll numbers are skipped.
    
    For any import file containing the same roll number multiple times,
    only one alumni record should exist after import.
    
    **Validates: Requirements 6.5**
    """
    # Use unique ID to create roll number for this test run
    unique_id = get_unique_id()
    roll_number = f'DUP{unique_id}'
    
    # Create a DataFrame with duplicate roll numbers but unique LinkedIn IDs
    data = {
        'Roll No.': [roll_number] * num_duplicates,
        'Name': [f'Student_{i}' for i in range(num_duplicates)],
        'LinkedIn ID': [f'dupstudent{unique_id}_{i}' for i in range(num_duplicates)]
    }
    df = pd.DataFrame(data)
    
    # Import with skip_duplicates=True
    summary = import_from_dataframe(
        db_session,
        df,
        queue_for_scraping=False,
        skip_duplicates=True
    )
    
    # Verify that only one record was created
    assert summary.new_records == 1
    assert summary.skipped_records == num_duplicates - 1
    
    # Verify only one record exists in database
    alumni = get_alumni_by_roll_number(db_session, roll_number)
    assert alumni is not None
    assert alumni.roll_number == roll_number


# =============================================================================
# Property 44: Import summary matches actual results
# Feature: alumni-management-system, Property 44: Import summary matches actual results
# Validates: Requirements 6.10
# =============================================================================


@given(
    num_new=st.integers(min_value=1, max_value=10),
    num_duplicates=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_44_import_summary_matches_actual_results(
    db_session,
    num_new: int,
    num_duplicates: int
):
    """
    Property 44: Import summary matches actual results.
    
    For any import operation, the summary counts for new records and
    updates should match the actual number of records created and updated.
    
    **Validates: Requirements 6.10**
    """
    # Use unique ID for this test run
    unique_id = get_unique_id()
    
    # First, create some existing records
    existing_data = {
        'Roll No.': [f'EXIST{unique_id}_{str(i).zfill(3)}' for i in range(num_duplicates)],
        'Name': [f'Existing_{i}' for i in range(num_duplicates)],
        'LinkedIn ID': [f'existing{unique_id}_{i}' for i in range(num_duplicates)]
    }
    existing_df = pd.DataFrame(existing_data)
    
    first_summary = import_from_dataframe(
        db_session,
        existing_df,
        queue_for_scraping=False,
        skip_duplicates=True
    )
    
    # Now import a mix of new and duplicate records
    mixed_data = {
        'Roll No.': (
            [f'NEW{unique_id}_{str(i).zfill(3)}' for i in range(num_new)] +
            [f'EXIST{unique_id}_{str(i).zfill(3)}' for i in range(num_duplicates)]
        ),
        'Name': (
            [f'New_{i}' for i in range(num_new)] +
            [f'Existing_{i}_Updated' for i in range(num_duplicates)]
        ),
        'LinkedIn ID': (
            [f'new{unique_id}_{i}' for i in range(num_new)] +
            [f'existing{unique_id}_{i}_updated' for i in range(num_duplicates)]
        )
    }
    mixed_df = pd.DataFrame(mixed_data)
    
    second_summary = import_from_dataframe(
        db_session,
        mixed_df,
        queue_for_scraping=False,
        skip_duplicates=True
    )
    
    # Verify summary matches actual results
    assert second_summary.total_rows == num_new + num_duplicates
    assert second_summary.new_records == num_new
    assert second_summary.skipped_records == num_duplicates
    
    # Verify the actual database state matches the summary
    for i in range(num_new):
        roll = f'NEW{unique_id}_{str(i).zfill(3)}'
        alumni = get_alumni_by_roll_number(db_session, roll)
        assert alumni is not None
        assert alumni.name == f'New_{i}'
    
    # Verify duplicates were skipped (not updated)
    for i in range(num_duplicates):
        roll = f'EXIST{unique_id}_{str(i).zfill(3)}'
        alumni = get_alumni_by_roll_number(db_session, roll)
        assert alumni is not None
        # Name should still be the original, not updated
        assert alumni.name == f'Existing_{i}'
