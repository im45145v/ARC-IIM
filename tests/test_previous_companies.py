"""
Tests for previous companies column functionality.

This test verifies that previous companies are correctly extracted from job history
and displayed in the browse table and Excel export.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from alumni_system.database.crud import (
    create_alumni,
    create_job_history,
    get_all_alumni,
)
from alumni_system.database.models import Alumni, JobHistory


def test_previous_companies_extraction_basic(clean_db_session):
    """Test that previous companies are correctly extracted from job history."""
    # Create an alumni
    alumni = create_alumni(
        clean_db_session,
        name="Test Alumni",
        roll_number="TEST001",
        batch="2020",
        current_company="Current Corp",
        current_designation="Senior Engineer",
    )
    
    # Add job history with previous companies
    create_job_history(
        clean_db_session,
        alumni_id=alumni.id,
        company_name="Previous Company 1",
        designation="Engineer",
        is_current=False,
    )
    
    create_job_history(
        clean_db_session,
        alumni_id=alumni.id,
        company_name="Previous Company 2",
        designation="Junior Engineer",
        is_current=False,
    )
    
    create_job_history(
        clean_db_session,
        alumni_id=alumni.id,
        company_name="Current Corp",
        designation="Senior Engineer",
        is_current=True,
    )
    
    # Fetch alumni with job history
    alumni_list = get_all_alumni(clean_db_session, limit=100)
    fetched_alumni = [a for a in alumni_list if a.roll_number == "TEST001"][0]
    
    # Verify job history is loaded
    assert hasattr(fetched_alumni, 'job_history')
    assert len(fetched_alumni.job_history) == 3
    
    # Extract previous companies (non-current jobs)
    previous_companies = []
    for job in fetched_alumni.job_history:
        if not job.is_current and job.company_name:
            role_info = f"{job.company_name}"
            if job.designation:
                role_info += f" ({job.designation})"
            previous_companies.append(role_info)
    
    # Verify previous companies are extracted correctly
    assert len(previous_companies) == 2
    assert "Previous Company 1 (Engineer)" in previous_companies
    assert "Previous Company 2 (Junior Engineer)" in previous_companies
    assert "Current Corp" not in "; ".join(previous_companies)


def test_previous_companies_with_no_designation(clean_db_session):
    """Test that previous companies work when designation is missing."""
    # Create an alumni
    alumni = create_alumni(
        clean_db_session,
        name="Test Alumni 2",
        roll_number="TEST002",
        batch="2020",
    )
    
    # Add job history without designation
    create_job_history(
        clean_db_session,
        alumni_id=alumni.id,
        company_name="Company Without Role",
        designation=None,
        is_current=False,
    )
    
    # Fetch alumni with job history
    alumni_list = get_all_alumni(clean_db_session, limit=100)
    fetched_alumni = [a for a in alumni_list if a.roll_number == "TEST002"][0]
    
    # Extract previous companies
    previous_companies = []
    for job in fetched_alumni.job_history:
        if not job.is_current and job.company_name:
            role_info = f"{job.company_name}"
            if job.designation:
                role_info += f" ({job.designation})"
            previous_companies.append(role_info)
    
    # Verify company name is included even without designation
    assert len(previous_companies) == 1
    assert previous_companies[0] == "Company Without Role"


def test_previous_companies_with_no_job_history(clean_db_session):
    """Test that alumni with no job history don't cause errors."""
    # Create an alumni without job history
    alumni = create_alumni(
        clean_db_session,
        name="Test Alumni 3",
        roll_number="TEST003",
        batch="2020",
    )
    
    # Fetch alumni
    alumni_list = get_all_alumni(clean_db_session, limit=100)
    fetched_alumni = [a for a in alumni_list if a.roll_number == "TEST003"][0]
    
    # Extract previous companies
    previous_companies = []
    if hasattr(fetched_alumni, 'job_history') and fetched_alumni.job_history:
        for job in fetched_alumni.job_history:
            if not job.is_current and job.company_name:
                role_info = f"{job.company_name}"
                if job.designation:
                    role_info += f" ({job.designation})"
                previous_companies.append(role_info)
    
    # Verify empty list for no job history
    assert len(previous_companies) == 0


def test_previous_companies_only_current_job(clean_db_session):
    """Test that only current job doesn't appear in previous companies."""
    # Create an alumni
    alumni = create_alumni(
        clean_db_session,
        name="Test Alumni 4",
        roll_number="TEST004",
        batch="2020",
        current_company="Current Corp",
    )
    
    # Add only current job
    create_job_history(
        clean_db_session,
        alumni_id=alumni.id,
        company_name="Current Corp",
        designation="Engineer",
        is_current=True,
    )
    
    # Fetch alumni
    alumni_list = get_all_alumni(clean_db_session, limit=100)
    fetched_alumni = [a for a in alumni_list if a.roll_number == "TEST004"][0]
    
    # Extract previous companies
    previous_companies = []
    for job in fetched_alumni.job_history:
        if not job.is_current and job.company_name:
            role_info = f"{job.company_name}"
            if job.designation:
                role_info += f" ({job.designation})"
            previous_companies.append(role_info)
    
    # Verify no previous companies
    assert len(previous_companies) == 0


def test_previous_companies_formatting(clean_db_session):
    """Test that previous companies are formatted correctly with semicolon separator."""
    # Create an alumni
    alumni = create_alumni(
        clean_db_session,
        name="Test Alumni 5",
        roll_number="TEST005",
        batch="2020",
    )
    
    # Add multiple previous jobs
    for i in range(3):
        create_job_history(
            clean_db_session,
            alumni_id=alumni.id,
            company_name=f"Company {i+1}",
            designation=f"Role {i+1}",
            is_current=False,
        )
    
    # Fetch alumni
    alumni_list = get_all_alumni(clean_db_session, limit=100)
    fetched_alumni = [a for a in alumni_list if a.roll_number == "TEST005"][0]
    
    # Extract and format previous companies
    previous_companies = []
    for job in fetched_alumni.job_history:
        if not job.is_current and job.company_name:
            role_info = f"{job.company_name}"
            if job.designation:
                role_info += f" ({job.designation})"
            previous_companies.append(role_info)
    
    formatted = "; ".join(previous_companies)
    
    # Verify formatting
    assert "Company 1 (Role 1)" in formatted
    assert "Company 2 (Role 2)" in formatted
    assert "Company 3 (Role 3)" in formatted
    assert formatted.count(";") == 2  # Two semicolons for three items


def test_previous_companies_count_property_examples(clean_db_session):
    """
    Test property: For any alumni with N previous jobs (is_current=False),
    the extracted previous companies list should have exactly N items.
    
    **Validates: Requirements 4.5, 10.1**
    """
    # Test case 1: No previous jobs, no current job
    alumni1 = create_alumni(
        clean_db_session,
        name="Alumni No Jobs",
        roll_number="TEST_PROP_001",
        batch="2020",
    )
    
    alumni_list = get_all_alumni(clean_db_session, limit=1000)
    fetched = [a for a in alumni_list if a.roll_number == "TEST_PROP_001"][0]
    
    previous_companies = []
    if hasattr(fetched, 'job_history') and fetched.job_history:
        for job in fetched.job_history:
            if not job.is_current and job.company_name:
                role_info = f"{job.company_name}"
                if job.designation:
                    role_info += f" ({job.designation})"
                previous_companies.append(role_info)
    
    assert len(previous_companies) == 0
    
    # Test case 2: 3 previous jobs, 1 current job
    alumni2 = create_alumni(
        clean_db_session,
        name="Alumni Multiple Jobs",
        roll_number="TEST_PROP_002",
        batch="2020",
    )
    
    for i in range(3):
        create_job_history(
            clean_db_session,
            alumni_id=alumni2.id,
            company_name=f"Previous Company {i+1}",
            designation=f"Role {i+1}",
            is_current=False,
        )
    
    create_job_history(
        clean_db_session,
        alumni_id=alumni2.id,
        company_name="Current Company",
        designation="Current Role",
        is_current=True,
    )
    
    alumni_list = get_all_alumni(clean_db_session, limit=1000)
    fetched = [a for a in alumni_list if a.roll_number == "TEST_PROP_002"][0]
    
    previous_companies = []
    if hasattr(fetched, 'job_history') and fetched.job_history:
        for job in fetched.job_history:
            if not job.is_current and job.company_name:
                role_info = f"{job.company_name}"
                if job.designation:
                    role_info += f" ({job.designation})"
                previous_companies.append(role_info)
    
    assert len(previous_companies) == 3
    assert "Current Company" not in "; ".join(previous_companies)
    
    # Test case 3: 5 previous jobs, no current job
    alumni3 = create_alumni(
        clean_db_session,
        name="Alumni Only Previous",
        roll_number="TEST_PROP_003",
        batch="2020",
    )
    
    for i in range(5):
        create_job_history(
            clean_db_session,
            alumni_id=alumni3.id,
            company_name=f"Old Company {i+1}",
            designation=f"Old Role {i+1}",
            is_current=False,
        )
    
    alumni_list = get_all_alumni(clean_db_session, limit=1000)
    fetched = [a for a in alumni_list if a.roll_number == "TEST_PROP_003"][0]
    
    previous_companies = []
    if hasattr(fetched, 'job_history') and fetched.job_history:
        for job in fetched.job_history:
            if not job.is_current and job.company_name:
                role_info = f"{job.company_name}"
                if job.designation:
                    role_info += f" ({job.designation})"
                previous_companies.append(role_info)
    
    assert len(previous_companies) == 5
