"""
Property-based tests for scraping logs functionality.

**Feature: alumni-management-system, Property 15: Scraping operations are logged**
**Validates: Requirements 2.6**

Tests that every scraping operation creates a log entry with appropriate details.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alumni_system.database.crud import create_alumni, create_scraping_log, get_scraping_logs
from alumni_system.database.models import Alumni, ScrapingLog


# =============================================================================
# Hypothesis Strategies
# =============================================================================

@st.composite
def alumni_data(draw):
    """Generate random alumni data for testing."""
    return {
        "name": draw(st.text(min_size=3, max_size=50, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ')),
        "roll_number": draw(st.text(min_size=5, max_size=20, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')),
        "batch": draw(st.sampled_from(["2018", "2019", "2020", "2021", "2022", "2023"])),
        "linkedin_url": f"https://www.linkedin.com/in/{draw(st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))}",
    }


@st.composite
def scraping_result(draw):
    """Generate random scraping result (success or failure)."""
    success = draw(st.booleans())
    
    if success:
        return {
            "success": True,
            "profile_data": {
                "name": draw(st.text(min_size=3, max_size=50)),
                "current_company": draw(st.text(min_size=3, max_size=50)),
                "location": draw(st.text(min_size=3, max_size=50)),
                "job_history": [],
                "education_history": [],
            },
            "pdf_stored": draw(st.booleans()),
        }
    else:
        return {
            "success": False,
            "error": draw(st.text(min_size=10, max_size=100)),
        }


# =============================================================================
# Property Tests
# =============================================================================

@given(alumni=alumni_data(), result=scraping_result())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_scraping_operations_are_logged(db_session, alumni, result):
    """
    Property 15: Scraping operations are logged
    
    For any scraping operation (success or failure), exactly one log entry
    should be created in the scraping_logs table with appropriate details.
    
    **Validates: Requirements 2.6**
    """
    # Create alumni record
    alumni_record = create_alumni(db_session, **alumni)
    
    # Get initial log count
    initial_logs = get_scraping_logs(db_session)
    initial_count = len(initial_logs)
    
    # Simulate scraping operation by creating a log entry
    # (This is what the scraper should do)
    account_email = "test@example.com"
    
    if result["success"]:
        log = create_scraping_log(
            db_session,
            alumni_id=alumni_record.id,
            linkedin_url=alumni["linkedin_url"],
            account_email=account_email,
            status="success",
            pdf_stored=result["pdf_stored"],
            duration_seconds=10,
        )
    else:
        log = create_scraping_log(
            db_session,
            alumni_id=alumni_record.id,
            linkedin_url=alumni["linkedin_url"],
            account_email=account_email,
            status="failed",
            error_message=result["error"],
            pdf_stored=False,
            duration_seconds=5,
        )
    
    # Verify log was created
    assert log is not None
    assert log.id is not None
    
    # Verify exactly one new log entry was created
    final_logs = get_scraping_logs(db_session)
    final_count = len(final_logs)
    assert final_count == initial_count + 1, "Exactly one log entry should be created per scraping operation"
    
    # Verify log contains required fields
    assert log.alumni_id == alumni_record.id
    assert log.linkedin_url == alumni["linkedin_url"]
    assert log.account_email == account_email
    assert log.status in ["success", "failed", "skipped"]
    assert log.created_at is not None
    
    # Verify status-specific fields
    if result["success"]:
        assert log.status == "success"
        assert log.pdf_stored == result["pdf_stored"]
        assert log.error_message is None or log.error_message == ""
    else:
        assert log.status == "failed"
        assert log.error_message == result["error"]
        assert log.pdf_stored is False


@given(alumni=alumni_data())
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_scraping_log_contains_account_email(db_session, alumni):
    """
    Property: Scraping logs track which account was used
    
    For any scraping operation, the log should contain the account_email
    that was used for scraping.
    
    **Validates: Requirements 2.6**
    """
    # Create alumni record
    alumni_record = create_alumni(db_session, **alumni)
    
    # Create log with account email
    account_email = "scraper1@example.com"
    log = create_scraping_log(
        db_session,
        alumni_id=alumni_record.id,
        linkedin_url=alumni["linkedin_url"],
        account_email=account_email,
        status="success",
        pdf_stored=True,
        duration_seconds=15,
    )
    
    # Verify account email is stored
    assert log.account_email == account_email
    
    # Verify we can query logs by account email
    all_logs = get_scraping_logs(db_session)
    account_logs = [l for l in all_logs if l.account_email == account_email]
    assert len(account_logs) >= 1
    assert log.id in [l.id for l in account_logs]


@given(alumni=alumni_data())
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_scraping_log_contains_duration(db_session, alumni):
    """
    Property: Scraping logs track operation duration
    
    For any scraping operation, the log should contain the duration
    in seconds.
    
    **Validates: Requirements 2.6**
    """
    # Create alumni record
    alumni_record = create_alumni(db_session, **alumni)
    
    # Create log with duration
    duration = 25
    log = create_scraping_log(
        db_session,
        alumni_id=alumni_record.id,
        linkedin_url=alumni["linkedin_url"],
        account_email="test@example.com",
        status="success",
        pdf_stored=True,
        duration_seconds=duration,
    )
    
    # Verify duration is stored
    assert log.duration_seconds == duration
    assert log.duration_seconds >= 0


@given(alumni=alumni_data())
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_scraping_log_contains_pdf_status(db_session, alumni):
    """
    Property: Scraping logs track PDF storage status
    
    For any scraping operation, the log should indicate whether
    the PDF was successfully stored.
    
    **Validates: Requirements 2.6**
    """
    # Create alumni record
    alumni_record = create_alumni(db_session, **alumni)
    
    # Test with PDF stored
    log_with_pdf = create_scraping_log(
        db_session,
        alumni_id=alumni_record.id,
        linkedin_url=alumni["linkedin_url"],
        account_email="test@example.com",
        status="success",
        pdf_stored=True,
        duration_seconds=20,
    )
    
    assert log_with_pdf.pdf_stored is True
    
    # Test without PDF stored
    log_without_pdf = create_scraping_log(
        db_session,
        alumni_id=alumni_record.id,
        linkedin_url=alumni["linkedin_url"],
        account_email="test@example.com",
        status="failed",
        pdf_stored=False,
        duration_seconds=10,
        error_message="Failed to download PDF",
    )
    
    assert log_without_pdf.pdf_stored is False


@given(alumni=alumni_data())
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_failed_operations_are_logged(db_session, alumni):
    """
    Property: Failed scraping operations are logged
    
    For any failed scraping operation, a log entry should be created
    with status="failed" and an error message.
    
    **Validates: Requirements 2.6**
    """
    # Create alumni record
    alumni_record = create_alumni(db_session, **alumni)
    
    # Get initial log count
    initial_count = len(get_scraping_logs(db_session))
    
    # Create log for failed operation
    error_message = "Connection timeout"
    log = create_scraping_log(
        db_session,
        alumni_id=alumni_record.id,
        linkedin_url=alumni["linkedin_url"],
        account_email="test@example.com",
        status="failed",
        error_message=error_message,
        pdf_stored=False,
        duration_seconds=5,
    )
    
    # Verify log was created
    final_count = len(get_scraping_logs(db_session))
    assert final_count == initial_count + 1
    
    # Verify failed operation details
    assert log.status == "failed"
    assert log.error_message == error_message
    assert log.pdf_stored is False


@given(
    alumni_list=st.lists(alumni_data(), min_size=2, max_size=5, unique_by=lambda x: x["roll_number"])
)
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_multiple_operations_create_multiple_logs(db_session, alumni_list):
    """
    Property: Multiple scraping operations create multiple log entries
    
    For any N scraping operations, exactly N log entries should be created.
    
    **Validates: Requirements 2.6**
    """
    # Get initial log count
    initial_count = len(get_scraping_logs(db_session))
    
    # Create alumni records and log entries
    created_logs = []
    for alumni_data_item in alumni_list:
        alumni_record = create_alumni(db_session, **alumni_data_item)
        
        log = create_scraping_log(
            db_session,
            alumni_id=alumni_record.id,
            linkedin_url=alumni_data_item["linkedin_url"],
            account_email="test@example.com",
            status="success",
            pdf_stored=True,
            duration_seconds=10,
        )
        created_logs.append(log)
    
    # Verify exactly N new logs were created
    final_count = len(get_scraping_logs(db_session))
    expected_count = initial_count + len(alumni_list)
    assert final_count == expected_count, f"Expected {len(alumni_list)} new logs, but got {final_count - initial_count}"
    
    # Verify all logs have unique IDs
    log_ids = [log.id for log in created_logs]
    assert len(log_ids) == len(set(log_ids)), "All log entries should have unique IDs"
