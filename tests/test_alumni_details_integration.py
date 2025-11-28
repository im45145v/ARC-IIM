"""
Integration tests for alumni details page functionality.

Tests the complete alumni details page workflow including:
- Displaying all job history records
- Showing current position indicator
- Calculating summary statistics
- Displaying education history
- Showing PDF download link
"""

import uuid
from datetime import datetime, timedelta

import pytest

from alumni_system.database.crud import (
    create_alumni,
    create_education_history,
    create_job_history,
    get_alumni_by_id,
    get_education_history_by_alumni,
    get_job_history_by_alumni,
)


def test_alumni_details_displays_all_job_history(db_session):
    """Test that alumni details page displays all job history records."""
    # Create alumni
    alumni = create_alumni(
        db_session,
        roll_number=str(uuid.uuid4())[:20],
        name="Test Alumni",
        batch="2020",
        current_company="Google",
        current_designation="Software Engineer",
    )
    
    # Create multiple job history records
    jobs = []
    for i in range(5):
        job = create_job_history(
            db_session,
            alumni_id=alumni.id,
            company_name=f"Company {i}",
            designation=f"Role {i}",
            location="Bangalore",
            start_date=datetime.now() - timedelta(days=365 * (5 - i)),
            end_date=datetime.now() - timedelta(days=365 * (4 - i)) if i < 4 else None,
            is_current=(i == 4),
            employment_type="Full-time",
        )
        jobs.append(job)
    
    # Fetch job history (simulating what the detail view does)
    fetched_jobs = get_job_history_by_alumni(db_session, alumni.id)
    
    # Verify all jobs are returned
    assert len(fetched_jobs) == 5
    
    # Verify jobs are sorted by start_date descending (most recent first)
    for i in range(len(fetched_jobs) - 1):
        assert fetched_jobs[i].start_date >= fetched_jobs[i + 1].start_date


def test_alumni_details_indicates_current_position(db_session):
    """Test that current position is properly indicated in job history."""
    # Create alumni
    alumni = create_alumni(
        db_session,
        roll_number=str(uuid.uuid4())[:20],
        name="Test Alumni",
        batch="2020",
    )
    
    # Create job history with one current position
    create_job_history(
        db_session,
        alumni_id=alumni.id,
        company_name="Old Company",
        designation="Junior Engineer",
        start_date=datetime.now() - timedelta(days=730),
        end_date=datetime.now() - timedelta(days=365),
        is_current=False,
        employment_type="Full-time",
    )
    
    current_job = create_job_history(
        db_session,
        alumni_id=alumni.id,
        company_name="Current Company",
        designation="Senior Engineer",
        start_date=datetime.now() - timedelta(days=365),
        end_date=None,
        is_current=True,
        employment_type="Full-time",
    )
    
    # Fetch job history
    fetched_jobs = get_job_history_by_alumni(db_session, alumni.id)
    
    # Verify current position is identifiable
    current_positions = [job for job in fetched_jobs if job.is_current]
    assert len(current_positions) == 1
    assert current_positions[0].id == current_job.id
    assert current_positions[0].end_date is None


def test_alumni_details_calculates_summary_statistics(db_session):
    """Test that summary statistics are correctly calculated."""
    # Create alumni
    alumni = create_alumni(
        db_session,
        roll_number=str(uuid.uuid4())[:20],
        name="Test Alumni",
        batch="2020",
    )
    
    # Create job history at multiple companies
    companies = ["Google", "Microsoft", "Google", "Amazon", "Microsoft"]
    for i, company in enumerate(companies):
        create_job_history(
            db_session,
            alumni_id=alumni.id,
            company_name=company,
            designation=f"Role {i}",
            start_date=datetime.now() - timedelta(days=365 * (5 - i)),
            end_date=datetime.now() - timedelta(days=365 * (4 - i)) if i < 4 else None,
            is_current=(i == 4),
            employment_type="Full-time",
        )
    
    # Fetch job history
    fetched_jobs = get_job_history_by_alumni(db_session, alumni.id)
    
    # Calculate statistics (as the detail view would)
    total_positions = len(fetched_jobs)
    unique_companies = len(set(job.company_name for job in fetched_jobs))
    
    # Verify statistics
    assert total_positions == 5, "Should have 5 total positions"
    assert unique_companies == 3, "Should have 3 unique companies (Google, Microsoft, Amazon)"


def test_alumni_details_displays_education_history(db_session):
    """Test that education history is displayed."""
    # Create alumni
    alumni = create_alumni(
        db_session,
        roll_number=str(uuid.uuid4())[:20],
        name="Test Alumni",
        batch="2020",
    )
    
    # Create education history records
    education_records = []
    for i in range(3):
        edu = create_education_history(
            db_session,
            alumni_id=alumni.id,
            institution_name=f"University {i}",
            degree="B.Tech" if i == 0 else "M.Tech",
            field_of_study="Computer Science",
            start_year=2015 + i * 4,
            end_year=2019 + i * 4,
            grade="A",
        )
        education_records.append(edu)
    
    # Fetch education history
    fetched_education = get_education_history_by_alumni(db_session, alumni.id)
    
    # Verify all education records are returned
    assert len(fetched_education) == 3


def test_alumni_details_shows_pdf_link_when_available(db_session):
    """Test that PDF download link is shown when available."""
    # Create alumni with PDF URL
    alumni_with_pdf = create_alumni(
        db_session,
        roll_number=str(uuid.uuid4())[:20],
        name="Alumni With PDF",
        batch="2020",
        linkedin_pdf_url="https://example.com/pdfs/alumni_123.pdf",
    )
    
    # Create alumni without PDF URL
    alumni_without_pdf = create_alumni(
        db_session,
        roll_number=str(uuid.uuid4())[:20],
        name="Alumni Without PDF",
        batch="2020",
        linkedin_pdf_url=None,
    )
    
    # Fetch alumni
    fetched_with_pdf = get_alumni_by_id(db_session, alumni_with_pdf.id)
    fetched_without_pdf = get_alumni_by_id(db_session, alumni_without_pdf.id)
    
    # Verify PDF URL presence
    assert fetched_with_pdf.linkedin_pdf_url is not None
    assert fetched_with_pdf.linkedin_pdf_url == "https://example.com/pdfs/alumni_123.pdf"
    
    assert fetched_without_pdf.linkedin_pdf_url is None


def test_alumni_details_complete_workflow(db_session):
    """Test complete alumni details page workflow."""
    # Create alumni with all information
    alumni = create_alumni(
        db_session,
        roll_number=str(uuid.uuid4())[:20],
        name="Complete Alumni",
        batch="2020",
        current_company="Google",
        current_designation="Senior Engineer",
        location="Bangalore",
        personal_email="test@example.com",
        linkedin_url="https://linkedin.com/in/test",
        linkedin_pdf_url="https://example.com/pdfs/test.pdf",
    )
    
    # Create job history
    for i in range(3):
        create_job_history(
            db_session,
            alumni_id=alumni.id,
            company_name=f"Company {i}",
            designation=f"Role {i}",
            location="Bangalore",
            start_date=datetime.now() - timedelta(days=365 * (3 - i)),
            end_date=datetime.now() - timedelta(days=365 * (2 - i)) if i < 2 else None,
            is_current=(i == 2),
            employment_type="Full-time",
        )
    
    # Create education history
    create_education_history(
        db_session,
        alumni_id=alumni.id,
        institution_name="IIT Delhi",
        degree="B.Tech",
        field_of_study="Computer Science",
        start_year=2016,
        end_year=2020,
        grade="A",
    )
    
    # Fetch all data (simulating detail view)
    fetched_alumni = get_alumni_by_id(db_session, alumni.id)
    fetched_jobs = get_job_history_by_alumni(db_session, alumni.id)
    fetched_education = get_education_history_by_alumni(db_session, alumni.id)
    
    # Verify all data is present
    assert fetched_alumni is not None
    assert fetched_alumni.name == "Complete Alumni"
    assert fetched_alumni.linkedin_pdf_url is not None
    
    assert len(fetched_jobs) == 3
    assert any(job.is_current for job in fetched_jobs)
    
    assert len(fetched_education) == 1
    
    # Verify statistics
    total_positions = len(fetched_jobs)
    unique_companies = len(set(job.company_name for job in fetched_jobs))
    
    assert total_positions == 3
    assert unique_companies == 3
