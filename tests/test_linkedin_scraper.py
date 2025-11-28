"""
Property-based tests for LinkedIn scraper with multi-account support.

Tests checkpoint detection, account rotation, and retry logic.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from hypothesis import given, settings, strategies as st
from playwright.async_api import Page

from alumni_system.scraper.account_rotation import LinkedInAccount
from alumni_system.scraper.linkedin_scraper import LinkedInScraper


# Helper function to create mock accounts
def create_mock_account(account_id: str, email: str) -> LinkedInAccount:
    """Create a mock LinkedInAccount for testing."""
    return LinkedInAccount(
        id=account_id,
        email=email,
        password="test_password",
        profiles_scraped_today=0,
        is_flagged=False,
        last_used=None
    )


@pytest.mark.asyncio
@given(
    num_accounts=st.integers(min_value=2, max_value=5),
    checkpoint_account_index=st.integers(min_value=0, max_value=4),
    daily_limit=st.integers(min_value=50, max_value=100)
)
@settings(max_examples=100, deadline=None)
async def test_checkpoint_detection_triggers_account_rotation(num_accounts, checkpoint_account_index, daily_limit):
    """
    Feature: alumni-management-system, Property 6: Checkpoint detection triggers account rotation
    
    For any account that encounters a security checkpoint, the system should mark it 
    as flagged and select a different account for the next operation.
    
    Validates: Requirements 1.13
    """
    from alumni_system.scraper.account_rotation import AccountRotationManager
    
    # Ensure checkpoint_account_index is within bounds
    checkpoint_account_index = checkpoint_account_index % num_accounts
    
    # Create mock accounts
    accounts = [
        create_mock_account(str(i), f"account{i}@test.com")
        for i in range(num_accounts)
    ]
    
    # Create account rotation manager
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Get the account that will encounter checkpoint
    checkpoint_account = accounts[checkpoint_account_index]
    checkpoint_email = checkpoint_account.email
    
    # Verify account is not flagged initially
    assert not checkpoint_account.is_flagged
    
    # Create scraper with the checkpoint account
    scraper = LinkedInScraper(account=checkpoint_account)
    
    # Mock the browser and page
    with patch.object(scraper, '_browser', new=Mock()):
        with patch.object(scraper, '_context', new=Mock()):
            mock_page = AsyncMock(spec=Page)
            scraper._page = mock_page
            
            # Mock login to succeed initially
            mock_page.goto = AsyncMock()
            mock_page.fill = AsyncMock()
            mock_page.click = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            
            # First call to url returns feed (successful login)
            mock_page.url = "https://www.linkedin.com/feed"
            
            # Login should succeed
            await scraper.login()
            assert scraper._logged_in is True
            
            # Now simulate checkpoint on profile scrape
            mock_page.url = "https://www.linkedin.com/checkpoint/challenge"
            
            # Scraping should raise exception due to checkpoint
            checkpoint_detected = False
            try:
                await scraper.scrape_profile("https://www.linkedin.com/in/testuser")
            except Exception as e:
                if "checkpoint" in str(e).lower() or "challenge" in str(e).lower():
                    checkpoint_detected = True
                    # Mark the account as flagged (simulating what the orchestrator would do)
                    manager.mark_account_flagged(checkpoint_email)
            
            # Verify checkpoint was detected
            assert checkpoint_detected, "Checkpoint should have been detected"
            
            # Verify the account was marked as flagged
            assert checkpoint_account.is_flagged, "Account should be flagged after checkpoint"
            
            # Verify that getting next account returns a different account (if available)
            if num_accounts > 1:
                next_account = manager.get_next_account()
                assert next_account is not None, "Should have another available account"
                assert next_account.email != checkpoint_email, "Should rotate to a different account"
                assert not next_account.is_flagged, "Next account should not be flagged"
            else:
                # If only one account, should return None
                next_account = manager.get_next_account()
                assert next_account is None, "Should return None when all accounts are flagged"


@pytest.mark.asyncio
@given(
    max_retries=st.integers(min_value=1, max_value=5),
    fail_count=st.integers(min_value=0, max_value=10)
)
@settings(max_examples=100, deadline=None)
async def test_retry_limit_is_enforced(max_retries, fail_count):
    """
    Feature: alumni-management-system, Property 7: Retry limit is enforced
    
    For any scraping operation that fails, the system should retry exactly up to 
    the configured maximum retry count before marking it as failed.
    
    Validates: Requirements 1.14
    """
    # Create a scraper with a mock account
    account = create_mock_account("1", "test@test.com")
    scraper = LinkedInScraper(account=account)
    
    # Track actual retry attempts
    attempt_count = 0
    
    async def mock_goto_with_failure(*args, **kwargs):
        nonlocal attempt_count
        attempt_count += 1
        # Fail for the specified number of times, then succeed
        if attempt_count <= fail_count:
            raise Exception("Network error")
        # After fail_count attempts, succeed (don't raise)
    
    # Mock the browser and page
    with patch.object(scraper, '_browser', new=Mock()):
        with patch.object(scraper, '_context', new=Mock()):
            mock_page = AsyncMock(spec=Page)
            scraper._page = mock_page
            
            # Mock login to succeed
            mock_page.fill = AsyncMock()
            mock_page.click = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.url = "https://www.linkedin.com/feed"
            
            await scraper.login()
            
            # Mock goto to fail then succeed
            mock_page.goto = AsyncMock(side_effect=mock_goto_with_failure)
            mock_page.query_selector = AsyncMock(return_value=None)
            
            # Mock extraction methods to return empty data
            with patch.object(scraper, '_extract_basic_info', new=AsyncMock(return_value={})):
                with patch.object(scraper, '_extract_experience', new=AsyncMock(return_value=[])):
                    with patch.object(scraper, '_extract_education', new=AsyncMock(return_value=[])):
                        with patch.object(scraper, '_extract_contact_info', new=AsyncMock(return_value={})):
                            # Mock random delay to be instant for testing
                            with patch.object(scraper, '_random_delay', new=AsyncMock()):
                                # Attempt to scrape
                                result = await scraper.scrape_profile(
                                    "https://www.linkedin.com/in/testuser",
                                    max_retries=max_retries
                                )
                                
                                # If fail_count >= max_retries, all retries exhausted, should return None
                                if fail_count >= max_retries:
                                    assert result is None
                                    # Should have attempted exactly max_retries times
                                    assert attempt_count == max_retries
                                else:
                                    # Should succeed after fail_count + 1 attempts
                                    assert result is not None
                                    assert attempt_count == fail_count + 1


@pytest.mark.asyncio
async def test_scraper_tracks_account_email():
    """Test that scraper correctly tracks which account is being used."""
    account = create_mock_account("1", "test@example.com")
    scraper = LinkedInScraper(account=account)
    
    with patch.object(scraper, '_browser', new=Mock()):
        with patch.object(scraper, '_context', new=Mock()):
            mock_page = AsyncMock(spec=Page)
            scraper._page = mock_page
            
            mock_page.goto = AsyncMock()
            mock_page.fill = AsyncMock()
            mock_page.click = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.url = "https://www.linkedin.com/feed"
            
            await scraper.login()
            
            # Verify account email is tracked
            assert scraper.get_current_account_email() == "test@example.com"


@pytest.mark.asyncio
async def test_scraper_includes_account_email_in_profile_data():
    """Test that scraped profile data includes the account email used."""
    account = create_mock_account("1", "scraper@example.com")
    scraper = LinkedInScraper(account=account)
    
    with patch.object(scraper, '_browser', new=Mock()):
        with patch.object(scraper, '_context', new=Mock()):
            mock_page = AsyncMock(spec=Page)
            scraper._page = mock_page
            
            # Mock successful login
            mock_page.goto = AsyncMock()
            mock_page.fill = AsyncMock()
            mock_page.click = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.url = "https://www.linkedin.com/feed"
            
            await scraper.login()
            
            # Mock profile scraping
            mock_page.url = "https://www.linkedin.com/in/testuser"
            mock_page.query_selector = AsyncMock(return_value=None)
            
            # Mock the extraction methods
            with patch.object(scraper, '_extract_basic_info', new=AsyncMock(return_value={"name": "Test User"})):
                with patch.object(scraper, '_extract_experience', new=AsyncMock(return_value=[])):
                    with patch.object(scraper, '_extract_education', new=AsyncMock(return_value=[])):
                        with patch.object(scraper, '_extract_contact_info', new=AsyncMock(return_value={})):
                            with patch.object(scraper, '_random_delay', new=AsyncMock()):
                                profile_data = await scraper.scrape_profile("https://www.linkedin.com/in/testuser")
                                
                                # Verify account email is in profile data
                                assert profile_data is not None
                                assert profile_data["account_email"] == "scraper@example.com"


@pytest.mark.asyncio
async def test_checkpoint_in_pdf_download_raises_exception():
    """Test that checkpoint detection during PDF download raises exception."""
    account = create_mock_account("1", "test@example.com")
    scraper = LinkedInScraper(account=account)
    
    with patch.object(scraper, '_browser', new=Mock()):
        with patch.object(scraper, '_context', new=Mock()):
            mock_page = AsyncMock(spec=Page)
            scraper._page = mock_page
            
            # Mock successful login
            mock_page.goto = AsyncMock()
            mock_page.fill = AsyncMock()
            mock_page.click = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            mock_page.url = "https://www.linkedin.com/feed"
            
            await scraper.login()
            
            # Mock checkpoint during PDF download
            mock_page.url = "https://www.linkedin.com/checkpoint/challenge"
            
            with patch.object(scraper, '_random_delay', new=AsyncMock()):
                with pytest.raises(Exception) as exc_info:
                    await scraper.download_profile_pdf("https://www.linkedin.com/in/testuser")
                
                assert "checkpoint" in str(exc_info.value).lower()
