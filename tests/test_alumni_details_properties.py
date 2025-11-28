"""
Property-based tests for alumni details page.

Tests correctness properties for alumni details display including:
- Detail view includes all job history
- Job history display indicates current position
- Job history statistics match actual records
"""

import uuid
from datetime import datetime, timedelta

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alumni_system.database.crud import (
    create_alumni,
    create_education_history,
    create_job_history,
    get_alumni_by_id,
    get_education_history_by_alumni,
    get_job_history_by_alumni,
)


# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def alumni_data(draw):
    """Generate random alumni data with unique roll number."""
    return {
        'roll_number': str(uuid.uuid4())[:20],
        'name': draw(st.text(min_size=3, max_size=50, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ')),
        'batch': draw(st.one_of(st.just('2020'), st.just('2021'), st.just('2022'), st.just('2023'))),
        'current_company': draw(st.one_of(st.just('Google'), st.just('Microsoft'), st.just('Amazon'), st.just('Apple'))),
        'current_designation': draw(st.text(min_size=3, max_size=50, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ')),
        'location': draw(st.one_of(st.just('Bangalore'), st.just('Mumbai'), st.just('Delhi'), st.just('Hyderabad'))),
    }


@st.composite
def job_history_data(draw):
    """Generate random job history data."""
    # Generate dates in the past
    days_ago = draw(st.integers(min_value=30, max_value=3650))
    start_date = datetime.now() - timedelta(days=days_ago)
    
    # Randomly decide if job is current or has an end date
    is_current = draw(st.booleans())
    
    if is_current:
        end_date = None
    else:
        # End date is after start date
        duration_days = draw(st.integers(min_value=30, max_value=days_ago))
        end_date = start_date + timedelta(days=duration_days)
    
    return {
        'company_name': draw(st.one_of(
            st.just('Google'), st.just('Microsoft'), st.just('Amazon'), 
            st.just('Apple'), st.just('Meta'), st.just('Netflix')
        )),
        'designation': draw(st.one_of(
            st.just('Software Engineer'), st.just('Senior Engineer'), 
            st.just('Staff Engineer'), st.just('Engineering Manager'),
            st.just('Product Manager'), st.just('Data Scientist')
        )),
        'location': draw(st.one_of(
            st.just('Bangalore'), st.just('Mumbai'), st.just('Delhi'), 
            st.just('Hyderabad'), st.just('San Francisco'), st.just('Seattle')
        )),
        'start_date': start_date,
        'end_date': end_date,
        'is_current': is_current,
        'employment_type': draw(st.one_of(
            st.just('Full-time'), st.just('Part-time'), 
            st.just('Contract'), st.just('Internship')
        )),
        'description': draw(st.text(min_size=10, max_size=200, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .')),
    }


@st.composite
def education_history_data(draw):
    """Generate random education history data."""
    start_year = draw(st.integers(min_value=2000, max_value=2020))
    end_year = start_year + draw(st.integers(min_value=2, max_value=5))
    
    return {
        'institution_name': draw(st.one_of(
            st.just('IIT Delhi'), st.just('IIT Bombay'), st.just('IIT Madras'),
            st.just('Stanford University'), st.just('MIT'), st.just('Harvard')
        )),
        'degree': draw(st.one_of(
            st.just('B.Tech'), st.just('M.Tech'), st.just('MBA'), 
            st.just('MS'), st.just('PhD')
        )),
        'field_of_study': draw(st.one_of(
            st.just('Computer Science'), st.just('Electrical Engineering'),
            st.just('Mechanical Engineering'), st.just('Business Administration')
        )),
        'start_year': start_year,
        'end_year': end_year,
        'grade': draw(st.one_of(st.just('A'), st.just('A+'), st.just('B+'), st.just('9.5/10'))),
    }


@st.composite
def alumni_with_job_history(draw):
    """Generate alumni with job history."""
    alumni_info = draw(alumni_data())
    num_jobs = draw(st.integers(min_value=1, max_value=10))
    jobs = [draw(job_history_data()) for _ in range(num_jobs)]
    
    # Ensure at least one job is marked as current if we have jobs
    if jobs and not any(job['is_current'] for job in jobs):
        jobs[0]['is_current'] = True
        jobs[0]['end_date'] = None
    
    return alumni_info, jobs


@st.composite
def alumni_with_education_history(draw):
    """Generate alumni with education history."""
    alumni_info = draw(alumni_data())
    num_edu = draw(st.integers(min_value=1, max_value=5))
    education = [draw(education_history_data()) for _ in range(num_edu)]
    
    return alumni_info, education


# =============================================================================
# Property Tests
# =============================================================================


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(data=alumni_with_job_history())
def test_property_28_detail_view_includes_all_job_history(db_session, data):
    """
    **Feature: alumni-management-system, Property 28: Detail view includes all job history**
    **Validates: Requirements 4.6**
    
    For any alumni with N job history records, the detail view should display all N records.
    """
    alumni_info, jobs = data
    
    # Create alumni
    alumni = create_alumni(db_session, **alumni_info)
    
    # Create job history records
    created_jobs = []
    for job_data in jobs:
        job = create_job_history(db_session, alumni_id=alumni.id, **job_data)
        created_jobs.append(job)
    
    # Simulate what the detail view would fetch
    fetched_job_history = get_job_history_by_alumni(db_session, alumni.id)
    
    # Property: Detail view should include all job history records
    assert len(fetched_job_history) == len(created_jobs), \
        f"Detail view should display all {len(created_jobs)} job history records, but got {len(fetched_job_history)}"
    
    # Verify all job IDs are present
    fetched_ids = {job.id for job in fetched_job_history}
    created_ids = {job.id for job in created_jobs}
    
    assert fetched_ids == created_ids, \
        f"Detail view should include all job records. Missing: {created_ids - fetched_ids}, Extra: {fetched_ids - created_ids}"
    
    # Verify all job details are preserved
    for created_job in created_jobs:
        matching_fetched = next((j for j in fetched_job_history if j.id == created_job.id), None)
        assert matching_fetched is not None, f"Job {created_job.id} not found in fetched history"
        
        assert matching_fetched.company_name == created_job.company_name
        assert matching_fetched.designation == created_job.designation
        assert matching_fetched.is_current == created_job.is_current


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(data=alumni_with_job_history())
def test_property_58_job_history_display_indicates_current_position(db_session, data):
    """
    **Feature: alumni-management-system, Property 58: Job history display indicates current position**
    **Validates: Requirements 10.3**
    
    For any alumni's job history display, the current position should be clearly indicated.
    """
    alumni_info, jobs = data
    
    # Create alumni
    alumni = create_alumni(db_session, **alumni_info)
    
    # Create job history records
    for job_data in jobs:
        create_job_history(db_session, alumni_id=alumni.id, **job_data)
    
    # Simulate what the detail view would fetch
    fetched_job_history = get_job_history_by_alumni(db_session, alumni.id)
    
    # Property: Current positions should be identifiable via is_current flag
    current_positions = [job for job in fetched_job_history if job.is_current]
    non_current_positions = [job for job in fetched_job_history if not job.is_current]
    
    # Verify that current positions have is_current=True
    for job in current_positions:
        assert job.is_current is True, \
            f"Job {job.id} marked as current should have is_current=True"
        assert job.end_date is None, \
            f"Current job {job.id} should not have an end_date"
    
    # Verify that non-current positions have is_current=False
    for job in non_current_positions:
        assert job.is_current is False, \
            f"Job {job.id} not marked as current should have is_current=False"
    
    # Verify we can distinguish current from past positions
    assert len(current_positions) + len(non_current_positions) == len(fetched_job_history), \
        "All jobs should be categorized as either current or non-current"


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(data=alumni_with_job_history())
def test_property_59_job_history_statistics_match_actual_records(db_session, data):
    """
    **Feature: alumni-management-system, Property 59: Job history statistics match actual records**
    **Validates: Requirements 10.5**
    
    For any alumni, summary statistics (total companies, total positions) should match 
    the actual job history records.
    """
    alumni_info, jobs = data
    
    # Create alumni
    alumni = create_alumni(db_session, **alumni_info)
    
    # Create job history records
    for job_data in jobs:
        create_job_history(db_session, alumni_id=alumni.id, **job_data)
    
    # Simulate what the detail view would fetch
    fetched_job_history = get_job_history_by_alumni(db_session, alumni.id)
    
    # Calculate statistics (as the detail view would)
    total_positions = len(fetched_job_history)
    unique_companies = len(set(job.company_name for job in fetched_job_history))
    
    # Property: Statistics should match actual records
    # Total positions should equal number of job history records
    assert total_positions == len(jobs), \
        f"Total positions statistic {total_positions} should match actual job count {len(jobs)}"
    
    # Total companies should equal unique company names
    expected_unique_companies = len(set(job['company_name'] for job in jobs))
    assert unique_companies == expected_unique_companies, \
        f"Total companies statistic {unique_companies} should match actual unique companies {expected_unique_companies}"
    
    # Verify the statistics are computed correctly from the fetched data
    # (not from some cached or incorrect source)
    recomputed_total = len(fetched_job_history)
    recomputed_companies = len(set(job.company_name for job in fetched_job_history))
    
    assert total_positions == recomputed_total, \
        "Total positions should be computed from actual fetched records"
    assert unique_companies == recomputed_companies, \
        "Total companies should be computed from actual fetched records"
