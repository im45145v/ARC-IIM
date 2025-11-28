"""
Property-based tests for account rotation and rate limiting system.

Tests the AccountRotationManager and LinkedInAccount classes to ensure
they correctly handle multi-account rotation, rate limiting, and usage tracking.
"""

import os
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings, strategies as st

from alumni_system.scraper.account_rotation import AccountRotationManager, LinkedInAccount


# =============================================================================
# Property Test 2.1: Account loading from environment variables
# =============================================================================


@given(
    num_accounts=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=100)
def test_account_loading_from_environment(num_accounts):
    """
    Feature: alumni-management-system, Property 1: Account loading from environment variables
    
    For any set of numbered environment variables (LINKEDIN_EMAIL_N, LINKEDIN_PASSWORD_N),
    the system should load exactly N accounts where N is the highest consecutive number
    before a gap.
    
    Validates: Requirements 1.1
    """
    # Set up environment variables for N consecutive accounts
    env_vars = {}
    for i in range(1, num_accounts + 1):
        env_vars[f"LINKEDIN_EMAIL_{i}"] = f"test{i}@example.com"
        env_vars[f"LINKEDIN_PASSWORD_{i}"] = f"password{i}"
    
    with patch.dict(os.environ, env_vars, clear=False):
        manager = AccountRotationManager()
        
        # Should load exactly num_accounts accounts
        assert len(manager.accounts) == num_accounts
        
        # Verify each account has correct email
        for i in range(num_accounts):
            assert manager.accounts[i].email == f"test{i+1}@example.com"
            assert manager.accounts[i].password == f"password{i+1}"
            assert manager.accounts[i].id == str(i+1)


@given(
    num_accounts=st.integers(min_value=3, max_value=10),
    gap_position=st.integers(min_value=2, max_value=5)
)
@settings(max_examples=100)
def test_account_loading_stops_at_gap(num_accounts, gap_position):
    """
    Feature: alumni-management-system, Property 1: Account loading from environment variables
    
    Test that account loading stops at the first gap in the sequence.
    
    Validates: Requirements 1.1
    """
    # Ensure gap is within range and not at position 1
    if gap_position >= num_accounts:
        gap_position = num_accounts - 1
    if gap_position < 2:
        gap_position = 2
    
    # Set up environment variables with a gap
    env_vars = {}
    for i in range(1, num_accounts + 1):
        if i != gap_position:
            env_vars[f"LINKEDIN_EMAIL_{i}"] = f"test{i}@example.com"
            env_vars[f"LINKEDIN_PASSWORD_{i}"] = f"password{i}"
    
    with patch.dict(os.environ, env_vars, clear=False):
        manager = AccountRotationManager()
        
        # Should load only accounts before the gap
        expected_count = gap_position - 1
        assert len(manager.accounts) == expected_count


def test_account_loading_raises_error_when_no_accounts():
    """
    Test that AccountRotationManager raises an error when no accounts are configured.
    
    Validates: Requirements 1.1
    """
    # Clear all LinkedIn account environment variables
    env_vars = {k: v for k, v in os.environ.items() if not k.startswith('LINKEDIN_EMAIL_') and not k.startswith('LINKEDIN_PASSWORD_')}
    
    with patch.dict(os.environ, env_vars, clear=True):
        with pytest.raises(ValueError, match="No LinkedIn accounts configured"):
            AccountRotationManager()



# =============================================================================
# Property Test 2.2: Account selection from available pool
# =============================================================================


@given(
    num_accounts=st.integers(min_value=2, max_value=10),
    daily_limit=st.integers(min_value=10, max_value=100)
)
@settings(max_examples=100)
def test_account_selection_from_available_pool(num_accounts, daily_limit):
    """
    Feature: alumni-management-system, Property 2: Account selection from available pool
    
    For any rotation pool with at least one non-exhausted account, selecting the next
    account should return a non-exhausted account.
    
    Validates: Requirements 1.2
    """
    # Create accounts with varying usage
    accounts = []
    for i in range(num_accounts):
        # Make some accounts exhausted, some available
        profiles_scraped = daily_limit if i % 2 == 0 else 0
        account = LinkedInAccount(
            id=str(i+1),
            email=f"test{i+1}@example.com",
            password=f"password{i+1}",
            profiles_scraped_today=profiles_scraped,
            is_flagged=False
        )
        accounts.append(account)
    
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Get next account
    selected = manager.get_next_account()
    
    # Should return a non-exhausted account
    assert selected is not None
    assert selected.profiles_scraped_today < daily_limit
    assert not selected.is_flagged


@given(
    num_accounts=st.integers(min_value=1, max_value=10),
    daily_limit=st.integers(min_value=10, max_value=100)
)
@settings(max_examples=100)
def test_account_selection_returns_none_when_all_exhausted(num_accounts, daily_limit):
    """
    Feature: alumni-management-system, Property 2: Account selection from available pool
    
    When all accounts are exhausted, get_next_account should return None.
    
    Validates: Requirements 1.2
    """
    # Create accounts that are all exhausted
    accounts = []
    for i in range(num_accounts):
        account = LinkedInAccount(
            id=str(i+1),
            email=f"test{i+1}@example.com",
            password=f"password{i+1}",
            profiles_scraped_today=daily_limit,
            is_flagged=False
        )
        accounts.append(account)
    
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Should return None when all exhausted
    selected = manager.get_next_account()
    assert selected is None


@given(
    num_accounts=st.integers(min_value=2, max_value=10),
    daily_limit=st.integers(min_value=10, max_value=100)
)
@settings(max_examples=100)
def test_account_selection_skips_flagged_accounts(num_accounts, daily_limit):
    """
    Feature: alumni-management-system, Property 2: Account selection from available pool
    
    Flagged accounts should be skipped during selection.
    
    Validates: Requirements 1.2
    """
    # Create accounts with some flagged
    accounts = []
    for i in range(num_accounts):
        # Flag every other account
        is_flagged = (i % 2 == 0)
        account = LinkedInAccount(
            id=str(i+1),
            email=f"test{i+1}@example.com",
            password=f"password{i+1}",
            profiles_scraped_today=0,
            is_flagged=is_flagged
        )
        accounts.append(account)
    
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Get next account
    selected = manager.get_next_account()
    
    # Should return a non-flagged account
    if selected is not None:
        assert not selected.is_flagged



# =============================================================================
# Property Test 2.3: Account exhaustion triggers rotation
# =============================================================================


@given(
    num_accounts=st.integers(min_value=2, max_value=10),
    daily_limit=st.integers(min_value=10, max_value=100)
)
@settings(max_examples=100)
def test_account_exhaustion_triggers_rotation(num_accounts, daily_limit):
    """
    Feature: alumni-management-system, Property 3: Account exhaustion triggers rotation
    
    For any account that reaches its daily limit, the system should mark it as exhausted
    and the next selection should return a different account.
    
    Validates: Requirements 1.3
    """
    # Create accounts
    accounts = []
    for i in range(num_accounts):
        account = LinkedInAccount(
            id=str(i+1),
            email=f"test{i+1}@example.com",
            password=f"password{i+1}",
            profiles_scraped_today=0,
            is_flagged=False
        )
        accounts.append(account)
    
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Get first account
    first_account = manager.get_next_account()
    assert first_account is not None
    first_email = first_account.email
    
    # Exhaust the first account
    manager.mark_account_exhausted(first_email)
    
    # Get next account - should be different
    second_account = manager.get_next_account()
    
    # If there are other available accounts, should get a different one
    if num_accounts > 1:
        assert second_account is not None
        assert second_account.email != first_email


@given(
    num_accounts=st.integers(min_value=2, max_value=10),
    daily_limit=st.integers(min_value=10, max_value=100),
    usage_increment=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=100)
def test_account_reaches_limit_through_increments(num_accounts, daily_limit, usage_increment):
    """
    Feature: alumni-management-system, Property 3: Account exhaustion triggers rotation
    
    When an account reaches its limit through incremental usage, it should be
    considered exhausted.
    
    Validates: Requirements 1.3
    """
    # Create accounts
    accounts = []
    for i in range(num_accounts):
        account = LinkedInAccount(
            id=str(i+1),
            email=f"test{i+1}@example.com",
            password=f"password{i+1}",
            profiles_scraped_today=0,
            is_flagged=False
        )
        accounts.append(account)
    
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Get first account
    first_account = manager.get_next_account()
    assert first_account is not None
    
    # Increment usage until it reaches or exceeds the limit
    increments_needed = (daily_limit + usage_increment - 1) // usage_increment
    for _ in range(increments_needed):
        manager.increment_usage(first_account.email)
    
    # Account should now be exhausted
    # Try to get it again - should skip it if there are other accounts
    next_account = manager.get_next_account()
    
    if num_accounts > 1:
        # Should get a different account
        assert next_account is not None
        assert next_account.email != first_account.email



# =============================================================================
# Property Test 2.4: Account usage tracking is accurate
# =============================================================================


@given(
    num_accounts=st.integers(min_value=1, max_value=5),
    num_scrapes=st.integers(min_value=1, max_value=50),
    daily_limit=st.integers(min_value=50, max_value=100)
)
@settings(max_examples=100)
def test_account_usage_tracking_is_accurate(num_accounts, num_scrapes, daily_limit):
    """
    Feature: alumni-management-system, Property 8: Account usage tracking is accurate
    
    For any account that scrapes N profiles on a given day, the system should
    record exactly N for that account.
    
    Validates: Requirements 1.15
    """
    # Create accounts
    accounts = []
    for i in range(num_accounts):
        account = LinkedInAccount(
            id=str(i+1),
            email=f"test{i+1}@example.com",
            password=f"password{i+1}",
            profiles_scraped_today=0,
            is_flagged=False
        )
        accounts.append(account)
    
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Select an account and increment its usage
    account = accounts[0]
    initial_count = account.profiles_scraped_today
    
    for _ in range(num_scrapes):
        manager.increment_usage(account.email)
    
    # Verify the count is accurate
    assert account.profiles_scraped_today == initial_count + num_scrapes


@given(
    num_accounts=st.integers(min_value=2, max_value=5),
    scrapes_per_account=st.lists(st.integers(min_value=0, max_value=20), min_size=2, max_size=5),
    daily_limit=st.integers(min_value=50, max_value=100)
)
@settings(max_examples=100)
def test_usage_tracking_per_account_is_independent(num_accounts, scrapes_per_account, daily_limit):
    """
    Feature: alumni-management-system, Property 8: Account usage tracking is accurate
    
    Usage tracking for each account should be independent - incrementing one
    account should not affect others.
    
    Validates: Requirements 1.15
    """
    # Ensure we have the right number of scrape counts
    if len(scrapes_per_account) > num_accounts:
        scrapes_per_account = scrapes_per_account[:num_accounts]
    elif len(scrapes_per_account) < num_accounts:
        scrapes_per_account.extend([0] * (num_accounts - len(scrapes_per_account)))
    
    # Create accounts
    accounts = []
    for i in range(num_accounts):
        account = LinkedInAccount(
            id=str(i+1),
            email=f"test{i+1}@example.com",
            password=f"password{i+1}",
            profiles_scraped_today=0,
            is_flagged=False
        )
        accounts.append(account)
    
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Increment each account by its designated amount
    for i, num_scrapes in enumerate(scrapes_per_account):
        for _ in range(num_scrapes):
            manager.increment_usage(accounts[i].email)
    
    # Verify each account has the correct count
    for i, expected_count in enumerate(scrapes_per_account):
        assert accounts[i].profiles_scraped_today == expected_count


@given(
    daily_limit=st.integers(min_value=10, max_value=100)
)
@settings(max_examples=100)
def test_usage_stats_reflect_current_state(daily_limit):
    """
    Feature: alumni-management-system, Property 8: Account usage tracking is accurate
    
    The get_usage_stats method should accurately reflect the current state
    of all accounts.
    
    Validates: Requirements 1.15
    """
    # Create accounts with varying usage
    accounts = [
        LinkedInAccount(
            id="1",
            email="test1@example.com",
            password="password1",
            profiles_scraped_today=0,
            is_flagged=False
        ),
        LinkedInAccount(
            id="2",
            email="test2@example.com",
            password="password2",
            profiles_scraped_today=daily_limit // 2,
            is_flagged=False
        ),
        LinkedInAccount(
            id="3",
            email="test3@example.com",
            password="password3",
            profiles_scraped_today=daily_limit,
            is_flagged=True
        ),
    ]
    
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Get usage stats
    stats = manager.get_usage_stats()
    
    # Verify stats match account state
    assert stats["test1@example.com"]["profiles_scraped"] == 0
    assert stats["test1@example.com"]["available"] is True
    
    assert stats["test2@example.com"]["profiles_scraped"] == daily_limit // 2
    assert stats["test2@example.com"]["available"] is True
    
    assert stats["test3@example.com"]["profiles_scraped"] == daily_limit
    assert stats["test3@example.com"]["is_flagged"] is True
    assert stats["test3@example.com"]["available"] is False



# =============================================================================
# Property Test 2.5: Daily reset clears all counters
# =============================================================================


@given(
    num_accounts=st.integers(min_value=1, max_value=10),
    daily_limit=st.integers(min_value=10, max_value=100),
    usage_amounts=st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=10)
)
@settings(max_examples=100)
def test_daily_reset_clears_all_counters(num_accounts, daily_limit, usage_amounts):
    """
    Feature: alumni-management-system, Property 9: Daily reset clears all counters
    
    For any state of account usage, after a daily reset operation, all accounts
    should have usage count of zero.
    
    Validates: Requirements 1.16
    """
    # Ensure we have the right number of usage amounts
    if len(usage_amounts) > num_accounts:
        usage_amounts = usage_amounts[:num_accounts]
    elif len(usage_amounts) < num_accounts:
        usage_amounts.extend([0] * (num_accounts - len(usage_amounts)))
    
    # Create accounts with varying usage
    accounts = []
    for i in range(num_accounts):
        account = LinkedInAccount(
            id=str(i+1),
            email=f"test{i+1}@example.com",
            password=f"password{i+1}",
            profiles_scraped_today=usage_amounts[i],
            is_flagged=(i % 2 == 0)  # Flag some accounts
        )
        accounts.append(account)
    
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Perform daily reset
    manager.reset_daily_counters()
    
    # Verify all counters are zero and flags are cleared
    for account in manager.accounts:
        assert account.profiles_scraped_today == 0
        assert account.is_flagged is False


@given(
    num_accounts=st.integers(min_value=2, max_value=10),
    daily_limit=st.integers(min_value=10, max_value=100)
)
@settings(max_examples=100)
def test_daily_reset_makes_all_accounts_available(num_accounts, daily_limit):
    """
    Feature: alumni-management-system, Property 9: Daily reset clears all counters
    
    After a daily reset, all accounts should be available for selection
    (assuming they were not permanently disabled).
    
    Validates: Requirements 1.16
    """
    # Create accounts that are all exhausted and flagged
    accounts = []
    for i in range(num_accounts):
        account = LinkedInAccount(
            id=str(i+1),
            email=f"test{i+1}@example.com",
            password=f"password{i+1}",
            profiles_scraped_today=daily_limit,
            is_flagged=True
        )
        accounts.append(account)
    
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Before reset, no accounts should be available
    assert manager.get_next_account() is None
    
    # Perform daily reset
    manager.reset_daily_counters()
    
    # After reset, should be able to get an account
    selected = manager.get_next_account()
    assert selected is not None
    assert selected.profiles_scraped_today == 0
    assert not selected.is_flagged


@given(
    num_accounts=st.integers(min_value=1, max_value=10),
    daily_limit=st.integers(min_value=10, max_value=100)
)
@settings(max_examples=100, deadline=None)
def test_daily_reset_restores_full_capacity(num_accounts, daily_limit):
    """
    Feature: alumni-management-system, Property 9: Daily reset clears all counters
    
    After a daily reset, the total available capacity should equal
    num_accounts * daily_limit.
    
    Validates: Requirements 1.16
    """
    # Create accounts with varying usage
    accounts = []
    for i in range(num_accounts):
        account = LinkedInAccount(
            id=str(i+1),
            email=f"test{i+1}@example.com",
            password=f"password{i+1}",
            profiles_scraped_today=daily_limit // 2,
            is_flagged=False
        )
        accounts.append(account)
    
    manager = AccountRotationManager(accounts=accounts, daily_limit=daily_limit)
    
    # Perform daily reset
    manager.reset_daily_counters()
    
    # Total capacity should be num_accounts * daily_limit
    total_capacity = manager.get_total_available_capacity()
    assert total_capacity == num_accounts * daily_limit
