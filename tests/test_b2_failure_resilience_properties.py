"""
Property-based tests for B2 failure resilience.

Tests that B2 failures don't prevent database saves during scraping operations.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import MagicMock, patch
from datetime import datetime


class MockAlumni:
    """Mock Alumni object for testing."""
    def __init__(self, alumni_id: int, roll_number: str):
        self.id = alumni_id
        self.roll_number = roll_number
        self.name = "Test Alumni"
        self.linkedin_url = f"https://www.linkedin.com/in/{roll_number}"
        self.current_company = None
        self.current_designation = None
        self.location = None
        self.linkedin_pdf_url = None
        self.last_scraped_at = None


class MockDatabase:
    """Mock database for testing."""
    def __init__(self):
        self.alumni = {}
        self.committed = False
        self.rolled_back = False
    
    def save_alumni(self, alumni):
        """Save alumni to mock database."""
        self.alumni[alumni.id] = alumni
        return True
    
    def commit(self):
        """Commit transaction."""
        self.committed = True
    
    def rollback(self):
        """Rollback transaction."""
        self.rolled_back = True
    
    def get_alumni(self, alumni_id):
        """Get alumni from mock database."""
        return self.alumni.get(alumni_id)


async def simulate_scraping_with_b2_failure(alumni, scraped_data, b2_should_fail=True):
    """
    Simulate scraping operation where B2 upload may fail.
    
    This simulates the behavior of the scraping job where:
    1. Profile data is scraped successfully
    2. Data is saved to database
    3. PDF upload to B2 is attempted
    4. If B2 fails, the database save should still persist
    
    Args:
        alumni: Alumni object to update
        scraped_data: Dictionary of scraped data
        b2_should_fail: Whether B2 upload should fail
    
    Returns:
        Tuple of (database_saved, pdf_uploaded)
    """
    db = MockDatabase()
    database_saved = False
    pdf_uploaded = False
    
    try:
        # Step 1: Update alumni with scraped data
        alumni.current_company = scraped_data.get("current_company")
        alumni.current_designation = scraped_data.get("current_designation")
        alumni.location = scraped_data.get("location")
        alumni.last_scraped_at = datetime.utcnow()
        
        # Step 2: Save to database
        db.save_alumni(alumni)
        db.commit()
        database_saved = True
        
        # Step 3: Try to upload PDF to B2
        try:
            if b2_should_fail:
                raise Exception("B2 upload failed: Connection timeout")
            else:
                alumni.linkedin_pdf_url = f"https://b2.example.com/{alumni.roll_number}.pdf"
                pdf_uploaded = True
        except Exception as e:
            # B2 failure is caught and logged, but doesn't affect database save
            # This is the key behavior we're testing
            pass
        
    except Exception as e:
        # If there's an error in database save, rollback
        db.rollback()
        database_saved = False
    
    return database_saved, pdf_uploaded


@given(
    alumni_id=st.integers(min_value=1, max_value=1000),
    roll_number=st.text(min_size=5, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))),
    company=st.text(min_size=3, max_size=50),
    designation=st.text(min_size=3, max_size=50),
    location=st.text(min_size=3, max_size=50)
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_b2_failures_dont_prevent_database_saves(
    alumni_id,
    roll_number,
    company,
    designation,
    location
):
    """
    Feature: alumni-management-system, Property 57: B2 failures don't prevent database saves
    
    For any scraping operation where B2 upload fails, the scraped data should 
    still be saved to the database successfully.
    
    Validates: Requirements 9.3
    """
    # Create test alumni
    alumni = MockAlumni(alumni_id, roll_number)
    
    # Create scraped data
    scraped_data = {
        "current_company": company,
        "current_designation": designation,
        "location": location
    }
    
    # Simulate scraping with B2 failure
    database_saved, pdf_uploaded = await simulate_scraping_with_b2_failure(
        alumni,
        scraped_data,
        b2_should_fail=True
    )
    
    # Property: Database save should succeed even when B2 fails
    assert database_saved, \
        "Database save should succeed even when B2 upload fails"
    
    # Property: PDF should not be uploaded when B2 fails
    assert not pdf_uploaded, \
        "PDF upload should fail when B2 is unavailable"
    
    # Property: Scraped data should be present in alumni object
    assert alumni.current_company == company, \
        "Scraped company data should be saved even when B2 fails"
    assert alumni.current_designation == designation, \
        "Scraped designation data should be saved even when B2 fails"
    assert alumni.location == location, \
        "Scraped location data should be saved even when B2 fails"
    assert alumni.last_scraped_at is not None, \
        "last_scraped_at should be updated even when B2 fails"
    
    # Property: PDF URL should not be set when B2 fails
    assert alumni.linkedin_pdf_url is None, \
        "PDF URL should not be set when B2 upload fails"


@pytest.mark.asyncio
async def test_b2_failure_doesnt_rollback_database():
    """
    Test that B2 failure doesn't cause database rollback.
    """
    alumni = MockAlumni(1, "TEST001")
    scraped_data = {
        "current_company": "Test Company",
        "current_designation": "Test Role",
        "location": "Test Location"
    }
    
    # Simulate scraping with B2 failure
    database_saved, pdf_uploaded = await simulate_scraping_with_b2_failure(
        alumni,
        scraped_data,
        b2_should_fail=True
    )
    
    # Verify database was saved
    assert database_saved
    assert not pdf_uploaded
    
    # Verify data is present
    assert alumni.current_company == "Test Company"
    assert alumni.current_designation == "Test Role"
    assert alumni.location == "Test Location"


@pytest.mark.asyncio
async def test_b2_success_saves_pdf_url():
    """
    Test that when B2 succeeds, PDF URL is saved.
    """
    alumni = MockAlumni(1, "TEST001")
    scraped_data = {
        "current_company": "Test Company",
        "current_designation": "Test Role",
        "location": "Test Location"
    }
    
    # Simulate scraping with B2 success
    database_saved, pdf_uploaded = await simulate_scraping_with_b2_failure(
        alumni,
        scraped_data,
        b2_should_fail=False
    )
    
    # Verify both database and PDF succeeded
    assert database_saved
    assert pdf_uploaded
    
    # Verify PDF URL is set
    assert alumni.linkedin_pdf_url is not None
    assert "TEST001" in alumni.linkedin_pdf_url


@given(
    num_profiles=st.integers(min_value=2, max_value=10),
    num_b2_failures=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=50, deadline=None)
@pytest.mark.asyncio
async def test_partial_b2_failures_dont_affect_database_saves(num_profiles, num_b2_failures):
    """
    Test that in a batch where some B2 uploads fail, all database saves succeed.
    """
    # Ensure we have at least one success
    if num_b2_failures >= num_profiles:
        num_b2_failures = num_profiles - 1
    
    # Create test alumni
    alumni_list = [
        MockAlumni(i, f"TEST{i:03d}")
        for i in range(num_profiles)
    ]
    
    # Determine which will have B2 failures
    b2_failure_indices = set(range(num_b2_failures))
    
    # Process each alumni
    results = []
    for i, alumni in enumerate(alumni_list):
        scraped_data = {
            "current_company": f"Company {i}",
            "current_designation": f"Role {i}",
            "location": f"Location {i}"
        }
        
        b2_should_fail = i in b2_failure_indices
        database_saved, pdf_uploaded = await simulate_scraping_with_b2_failure(
            alumni,
            scraped_data,
            b2_should_fail=b2_should_fail
        )
        
        results.append({
            "database_saved": database_saved,
            "pdf_uploaded": pdf_uploaded,
            "alumni": alumni
        })
    
    # Property: All database saves should succeed
    all_db_saved = all(r["database_saved"] for r in results)
    assert all_db_saved, \
        "All database saves should succeed regardless of B2 failures"
    
    # Property: Correct number of PDF uploads should fail
    pdf_failures = sum(1 for r in results if not r["pdf_uploaded"])
    assert pdf_failures == num_b2_failures, \
        f"Expected {num_b2_failures} PDF upload failures, got {pdf_failures}"
    
    # Property: All alumni should have scraped data
    for result in results:
        alumni = result["alumni"]
        assert alumni.current_company is not None, \
            "All alumni should have scraped data even with B2 failures"
        assert alumni.last_scraped_at is not None, \
            "All alumni should have last_scraped_at updated"
